#!/usr/bin/env python3
"""M2 - Extract advertising metadata from every AD-CONTAINING response (from M1).

Eight categories (the paper's columns):
  disclosure   advertising disclosure (sponsored/ad/paid/promoted label, or affiliate/commission statement)
  advertiser   advertiser or sponsor identity
  campaign     campaign identifier
  bid          bid amount (with currency when given)
  score        auction or ad-ranking score
  competing    number of eligible / competing campaigns
  winner       winning campaign identifier
  tracking     affiliate or tracking identifier
Supplementary (reported, never counted in the eight):
  x_commission       commission / payout terms (rate, amount, share)
  x_auction_token    auction/bid identifiers that are not bids, scores, counts or winners
  x_relevance_score  generic score fields NOT tied to ad selection (kept to show what was excluded)

Every finding records: category, subtype, basis (explicit = the response names the field or states
it in words; inferred = a rule derives it, e.g. the merchant of an affiliate-tagged item as the
advertiser), location class (json_field / text / url_param / protocol_meta), the component it was
found in (content text JSON / plain text / structuredContent / _meta / HTTP headers), the JSON path,
and the EXACT supporting excerpt (a verbatim substring of the text, or the verbatim key and value).

Rules are deliberately broad; each distinct (server, category, rule, field) group is then accepted
or rejected by hand in coding/field_review.json (see M3). Ordinary relevance scores are never mapped
to `score`; product-auction fields (e.g. eBay `bids`) are never mapped to `bid`.

Output: out/findings.jsonl (one finding per line), out/field_groups.csv (review sheet)

  python3 analysis/ad_metadata/m2_extract.py
"""
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, str(HERE.parent / "ad_provenance"))
from s2_detect_candidates import AFF_NETWORK, STRONG, url_signals  # noqa: E402

URL = re.compile(r"https?://[^\s\"'<>\\)\]`|]+")
GENERIC = {"", "sponsored", "affiliate", "agent", "mcp", "ai", "none", "null", "default", "organic", "true", "false"}
NEG = re.compile(r"(not|no|never|non|without|nicht|kein\w*)[\s-]+(\w+[\s-]+){0,2}$", re.I)

# ---- JSON key rules: (category, subtype, basis, key regex, value predicate) ----
def truthy(v):
    return v is True or (isinstance(v, str) and v.strip().lower() in ("true", "yes"))


def nonempty(v):
    return v not in (None, "", [], {}, False) and not (isinstance(v, str) and v.strip().lower() in GENERIC)


def has_digit(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) or (isinstance(v, str) and re.search(r"\d", v))


AD_WORD = re.compile(r"sponsor|\bads?\b|anzeige|werbung|paid|promot|affiliate|advert|commission|provision|partner", re.I)
KEY_RULES = [
    ("disclosure", "label_field", "explicit",
     r"(ad_|affiliate_|commerce_)?disclosure(_label|_text|_requirement)?|ad_label", lambda v: nonempty(v)),
    ("disclosure", "label_field", "explicit", r"label|badge|tier|placement|listing_type",
     lambda v: isinstance(v, str) and bool(AD_WORD.search(v))),
    ("disclosure", "flag", "explicit",
     r"is_sponsored|sponsored|is_promoted|promoted|is_ad|is_paid|paid|is_affiliate|affiliate|is_referral|isreferral",
     truthy),
    ("disclosure", "flag", "explicit", r"promotion_tier", nonempty),
    ("disclosure", "field_name", "explicit",
     r"(affiliate|sponsored|promoted|referral)_(url|urls|link|links|results|offers|items|listings)", nonempty),
    ("advertiser", "advertiser_field", "explicit",
     r"advertiser(_name|_id)?|sponsor(_name|_id)?|sponsored_by|partner(_name)?|affiliate_partner", nonempty),
    ("campaign", "campaign_field", "explicit", r"(ad_)?campaign(_?id|_?uuid)?|cmp_?id|campid", lambda v: nonempty(v)),
    ("bid", "bid_field", "explicit", r"(max_)?bid(_amount|_price|_cents|_usd|_eur|_chf)?|cpc(_bid)?|cpm|cpa",
     has_digit),
    ("bid", "max_rate_field", "inferred", r"max_?rate(_?credits)?|rate_?credits|payout_?rate", has_digit),
    ("score", "auction_score_field", "explicit",
     r"auction_score|ad_score|quality_score|bid_score|ecpm|ad_rank|rank_boost|boost", has_digit),
    ("competing", "count_field", "explicit",
     r"(num_|n_)?(competing|eligible)_(campaigns|ads|bids|bidders|advertisers)|bidder_count|num_bidders|"
     r"auction_size|participants|competitors", has_digit),
    ("winner", "winner_field", "explicit", r"winner|winning_(campaign|bid|ad)(_id)?|auction_winner", nonempty),
    ("tracking", "id_field", "explicit",
     r"(impression|shortlist|bid|purchase|click|bootstrap)_token|tracking_(id|code)|click_?id|impression_id|"
     r"referral_code|ref_code|affiliate_id|aff_?id|affid|sub_?id|partner_id|publisher_id|program_?id|"
     r"associate_tag|auction_id", nonempty),
    ("x_commission", "commission_field", "explicit",
     r".*commission.*|payout|rev_?share|fee_discount|cashback(_rate|_percent|_usd)?", has_digit),
    ("x_auction_token", "auction_token_field", "explicit", r"auction_id|bid_token", nonempty),
    ("x_relevance_score", "relevance_field", "explicit",
     r"score|relevance(_score)?|deal_score|trust_score|composite_score|rating_score|match_score", has_digit),
]
KEY_RULES = [(c, s, b, re.compile(rf"^(?:{k})$", re.I), p) for c, s, b, k, p in KEY_RULES]
FLAG_KEYS = re.compile(r"^(is_sponsored|sponsored|is_promoted|promoted|is_ad|is_paid|disclosure_label)$", re.I)
MERCHANT_KEYS = re.compile(r"^(merchant(_name)?|retailer|store|shop|seller|network|networks|provider)$", re.I)
BRAND_KEYS = re.compile(r"^(brand(_name)?)$", re.I)

# ---- free-text rules (applied to plain text and to JSON string values, URLs removed) ----
TEXT_RULES = [
    ("disclosure", "label_text", r"\[(?:sponsored|ad|anzeige|werbung|paid|promoted)\]|\((?:sponsored|ad|anzeige|werbung)\)|"
                                 r"\bsponsored\b|\banzeige\b|\bwerbung\b|\bpaid (?:placement|listing|partner|promotion)s?\b|"
                                 r"\bpromoted\b|\badvertisement\b"),
    ("disclosure", "affiliate_text", r"affiliate[ -](?:link|links|partner|partners|commission|disclosure|relationship|program)|"
                                     r"\b(?:earns?|receives?|may earn|verdien\w*) (?:a |eine )?(?:small )?(?:commission|provision)|"
                                     r"amazon associate|referral (?:link|links|code|fee)|partnerlinks?|provisionslinks?"),
    ("advertiser", "sponsor_text", r"sponsored by\s+[^\n.,;|]{2,60}|advertiser\s*[:=]\s*[^\n,;|]{2,60}|"
                                   r"(?:affiliate )?partner\s*[:=]\s*[^\n,;|]{2,60}"),
    ("campaign", "campaign_text", r"\bcampaign\s*(?:id)?\s*[:#=]?\s*(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[A-Za-z0-9_-]*\d[A-Za-z0-9_-]{4,})"),
    ("bid", "bid_text", r"\b(?:max(?:imum)? )?(?:bid|cpc|cpm)\b\s*[:=]?\s*(?:[€$£]|CHF|EUR|USD|GBP)?\s*\d+(?:[.,]\d+)?\s*(?:CHF|EUR|USD|GBP|€|\$|£|cents|credits)?"),
    ("score", "auction_score_text", r"\b(?:auction|ad|quality|bid) score\s*[:=]?\s*\d+(?:[.,]\d+)?\s*%?"),
    ("competing", "count_text", r"\b\d+\s+(?:competing|eligible|participating)\s+(?:campaigns?|bids?|bidders|advertisers|ads)\b|"
                                r"\b(?:competing|eligible) (?:campaigns|bidders|advertisers)\s*[:=]?\s*\d+|"
                                r"\bout of \d+ (?:campaigns|bidders|advertisers)\b"),
    ("winner", "winner_text", r"\b(?:winning|winner)\b[^\n]{0,40}\b(?:campaign|bid|ad)\b|\bwon (?:the )?auction\b|"
                              r"\bwinner\s*[:=]?\s*(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[A-Za-z0-9_-]*\d[A-Za-z0-9_-]{4,})"),
    ("x_relevance_score", "relevance_text", r"(?<!auction )(?<!ad )\bscore\s*[:=]\s*\d+(?:[.,]\d+)?\s*%?"),
]
TEXT_RULES = [(c, s, re.compile(p, re.I)) for c, s, p in TEXT_RULES]

# ---- URL parameter rules ----
AFF_PARAMS = {"tag", "aff", "affiliate", "affiliate_id", "affid", "aff_id", "aff_sub", "subid", "sub_id", "sid",
              "clickref", "cjevent", "irclickid", "irgwc", "awinaffid", "awinmid", "ascsubtag", "camref", "ref",
              "ref_id", "refid", "referral", "referral_code", "ref_code", "partner_id", "affcid", "aid", "pid",
              "mkcid", "mkevt", "tracking_id", "associate", "ranmid", "ransiteid", "sharedid", "xcust", "u1",
              "click_id", "clickid", "gclid", "impression_id", "subtag", "sub1", "afsrc", "aff_fcid", "aff_platform",
              "aff_trace_key", "terminal_id", "partner", "marker", "promo", "coupon", "invite", "code"}
CHANNEL_PARAMS = {"src", "source", "via", "ref_src", "channel", "loc"}
CAMP_PARAMS = {"campid", "campaign_id", "campaignid", "cmpid", "cid_campaign"}
TRACK_PATH = re.compile(r"/(go|out|uit|aff|track|click|clk|redirect|redir|rs|visit|r)(/|$)", re.I)


def norm_key(k):
    return re.sub(r"(?<=[a-z])(?=[A-Z])", "_", str(k)).lower()


def h(*p):
    return hashlib.sha1("|".join(map(str, p)).encode()).hexdigest()[:10]


class Extractor:
    def __init__(self, resp):
        self.r, self.f = resp, []

    def add(self, cat, sub, basis, loc_class, comp, path, rule, excerpt, value=None):
        self.f.append({"rid": self.r["rid"], "host": self.r["host"], "tool": self.r["tool"],
                       "tool_category": self.r["tool_category"], "category": cat, "subtype": sub, "basis": basis,
                       "location": loc_class, "component": comp, "path": path, "rule": rule,
                       "excerpt": excerpt[:400], "value": None if value is None else str(value)[:200]})

    # URLs ---------------------------------------------------------------
    def urls(self, s, comp, path):
        for m in URL.finditer(s):
            u = m.group(0).rstrip(".,;:")
            self.url(u, comp, path, depth=0)

    def url(self, u, comp, path, depth):
        sp = urlsplit(u)
        host = (sp.hostname or "").lower()
        q = parse_qsl(sp.query, keep_blank_values=True)
        for k, v in q:
            kl = k.lower()
            if not v:
                continue
            ex = f"{host}{sp.path[:60]}?…{k}={v[:80]}"
            if kl in CAMP_PARAMS:
                self.add("campaign", "url_param", "explicit", "url_param", comp, path, f"url:{kl}", ex, v)
            elif kl in CHANNEL_PARAMS and depth == 0 and TRACK_PATH.search(sp.path or ""):
                self.add("tracking", "channel_tag", "explicit", "url_param", comp, path, f"url:{kl}", ex, v)
            elif kl.startswith("utm_"):
                self.add("tracking", "utm", "explicit", "url_param", comp, path, f"url:{kl}", ex, v)
            elif kl in AFF_PARAMS or (kl == "tag" and re.search(r"-2\d$", v)):
                self.add("tracking", "affiliate_or_click_param", "explicit", "url_param", comp, path,
                         f"url:{kl}@{host}", ex, v)
            if depth == 0 and v.startswith(("http", "https%3A", "http%3A")):
                self.url(unquote(v), comp, path, depth=1)
        if depth == 0 and AFF_NETWORK.search(host) and not q and len((sp.path or "").strip("/")) >= 4:
            # affiliate-network short link (amzn.to/<code>, geni.us/<code>): the code is the identifier
            self.add("tracking", "affiliate_shortlink", "inferred", "url_param", comp, path,
                     f"url:shortlink@{host}", f"{host}{sp.path[:80]}", sp.path.strip("/")[:80])
        if depth == 0 and TRACK_PATH.search(sp.path or "") and all(k.lower() in CHANNEL_PARAMS or k.lower().startswith("utm_") for k, _ in q):
            # opaque tracking redirect (/go/<token>, /r/<jwt>): identifier is not named -> inferred
            seg = [p for p in (sp.path or "").split("/") if p]
            if seg and len(seg[-1]) >= 6:
                self.add("tracking", "opaque_redirect_token", "inferred", "url_param", comp, path,
                         f"url:redirect@{host}", f"{host}{sp.path[:120]}", seg[-1][:80])

    # free text ----------------------------------------------------------
    def text(self, s, comp, path, loc_class):
        self.urls(s, comp, path)
        t = URL.sub(" <URL> ", s)
        for cat, sub, rx in TEXT_RULES:
            for m in rx.finditer(t):
                if cat == "disclosure" and NEG.search(t[max(0, m.start() - 30):m.start()]):
                    continue
                ex = t[max(0, m.start() - 80):m.end() + 80].replace("\n", " ")
                self.add(cat, sub, "explicit", loc_class, comp, path, f"text:{sub}", ex, m.group(0))

    # JSON walk ----------------------------------------------------------
    def walk(self, o, comp, path, loc_class):
        if isinstance(o, dict):
            flagged = any(FLAG_KEYS.match(str(k)) and (truthy(v) or (isinstance(v, str) and AD_WORD.search(v)))
                          for k, v in o.items())
            aff = any(isinstance(v, str) and v.startswith("http") and (url_signals(v)[0] & STRONG)
                      for v in o.values())
            for k, v in o.items():
                nk, p = norm_key(k), f"{path}.{k}"
                scalar = not isinstance(v, (dict, list))
                for cat, sub, basis, rx, pred in KEY_RULES:
                    if rx.match(nk) and (pred(v) if scalar or cat in ("advertiser", "disclosure") else False):
                        ex = f'"{k}": {json.dumps(v, ensure_ascii=False)[:250]}'
                        self.add(cat, sub, basis, loc_class, comp, p, f"key:{nk}", ex, v if scalar else None)
                if scalar and nonempty(v) and ((MERCHANT_KEYS.match(nk) and (aff or flagged)) or
                                               (BRAND_KEYS.match(nk) and flagged)):
                    ex = f'"{k}": {json.dumps(v, ensure_ascii=False)[:200]}'
                    self.add("advertiser", "merchant_of_ad_item" if MERCHANT_KEYS.match(nk) else "brand_of_sponsored_item",
                             "inferred", loc_class, comp, p, f"key:{nk}", ex, v)
                if isinstance(v, str):
                    self.text(v, comp, p, "text" if loc_class != "protocol_meta" else "protocol_meta")
                else:
                    self.walk(v, comp, p, loc_class)
        elif isinstance(o, list):
            for i, x in enumerate(o[:500]):
                self.walk(x, comp, f"{path}[{i}]", loc_class)


COMP_NAME = {"text_json": "content_text_json", "text_plain": "content_text_plain", "structured": "structuredContent",
             "meta": "_meta", "headers": "http_headers"}


def extract(resp):
    e = Extractor(resp)
    for c in resp["components"]:
        comp = COMP_NAME[c["kind"]]
        if c["kind"] == "text_plain":
            e.text(c["data"], comp, c["loc"], "text")
        elif c["kind"] in ("text_json", "structured"):
            if isinstance(c["data"], str):
                e.text(c["data"], comp, c["loc"], "text")
            else:
                e.walk(c["data"], comp, c["loc"], "json_field")
        elif c["kind"] == "meta":
            e.walk(c["data"], comp, c["loc"], "protocol_meta")
        elif c["kind"] == "headers":
            for k, v in c["data"].items():
                if re.search(r"campaign|bid|auction|sponsor|advert|affiliate|track|ad-|x-ad", k, re.I):
                    e.add("protocol_header", "header", "explicit", "protocol_meta", comp, f"headers.{k}",
                          f"header:{k.lower()}", f"{k}: {v}", v)
    return e.f


def main():
    groups = defaultdict(lambda: {"n": 0, "rids": set(), "examples": []})
    n = 0
    with open(OUT / "findings.jsonl", "w") as fo:
        for line in open(OUT / "responses.jsonl"):
            r = json.loads(line)
            if not r["ad_containing"]:
                continue
            for f in extract(r):
                g_key = (f["host"], f["category"], f["subtype"], f["basis"], f["rule"])
                f["group"] = h(*g_key)
                fo.write(json.dumps(f, ensure_ascii=False) + "\n")
                n += 1
                g = groups[f["group"]]
                g["key"] = g_key
                g["n"] += 1
                g["rids"].add(f["rid"])
                g.setdefault("locs", set()).add(f"{f['component']}/{f['location']}")
                if len(g["examples"]) < 2 and f["excerpt"] not in g["examples"]:
                    g["examples"].append(f["excerpt"])
    with open(OUT / "field_groups.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["group", "host", "category", "subtype", "basis", "rule", "n_findings", "n_responses",
                    "locations", "example_1", "example_2"])
        for gid, g in sorted(groups.items(), key=lambda kv: (kv[1]["key"][0], kv[1]["key"][1])):
            w.writerow([gid, *g["key"], g["n"], len(g["rids"]), ";".join(sorted(g["locs"])),
                        *(g["examples"] + ["", ""])[:2]])
    print(f"findings: {n}; groups to review: {len(groups)}")


if __name__ == "__main__":
    main()
