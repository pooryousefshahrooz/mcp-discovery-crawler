#!/usr/bin/env python3
"""S2 - High-recall, item-level ad-candidate detection over ALL recorded responses.

A candidate ITEM is either
  url   : one URL occurrence carrying a monetization signal, or
  label : one sponsored/promoted/ad marker attached to a returned item.
Each item gets a list of signals, each STRONG or WEAK:

  STRONG  aff_param      Amazon associate tag, aff/affiliate/aff_id/subid/clickref/cjevent/
                         irclickid/awinaffid/campid/ascsubtag/camref/ref_id/referral parameters
          aff_network    a host of a known affiliate network / affiliate redirector
          paid_utm       utm_medium in {cpc, ppc, paid, affiliate, display, sponsored, ad(s)}
          label          is_sponsored/is_promoted/promotion_tier/[Sponsored]/(Sponsored)/
                         disclosure_label Ad/"sponsored": true|[{ ... / Anzeige / Werbung
  WEAK    redirect_path  /go/ /out/ /aff/ /track/ /click /redirect /rs/ /visit/ /ref/ path on any host
          attrib_utm     any other utm_* parameter
          src_param      src=/source=/via=/agent= tagging the agent channel

Response-level affiliate DISCLOSURE text is recorded as a flag on the response, never as an item.

Items are grouped into SIGNATURES = (host, tool, kind, signal-set, url host, first path segment,
sorted param keys) - the unit of the hand review in S3. Every signature that has at least one
STRONG signal, or a WEAK signal from a redirect path, must be reviewed; attribution-only
signatures (attrib_utm / src_param alone) are reviewed as a class with examples.

Outputs: out/candidates.jsonl (one item per line), out/signatures.csv

  python3 analysis/ad_provenance/s2_detect_candidates.py
"""
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

URL = re.compile(r"https?://[^\s\"'<>\\)\]`|]+")
IMG = re.compile(r"\.(png|jpe?g|gif|webp|svg|ico|css|js|woff2?)(\?|$)", re.I)

AFF_KEYS = {"aff", "affiliate", "affiliate_id", "affid", "aff_id", "aff_sub", "subid", "sub_id",
            "clickref", "cjevent", "irclickid", "awinaffid", "campid", "ascsubtag", "camref",
            "ref_id", "refid", "referral", "referral_code", "ref_code", "partner_id", "affcid",
            "aid", "pid", "mkcid", "tracking_id", "associate", "ranmid", "ransiteid"}
AFF_NETWORK = re.compile(
    r"(^|\.)(amzn\.to|evyy\.net|sjv\.io|pxf\.io|ojrq\.net|awin1\.com|prf\.hn|anrdoezrs\.net|"
    r"dpbolvw\.net|kqzyfj\.net|tkqlhce\.com|jdoqocy\.com|shareasale\.com|linksynergy\.com|"
    r"skimresources\.com|redirectingat\.com|rstyle\.me|s\.click\.aliexpress\.com|tp\.media|"
    r"tp\.st|travelpayouts\.com|rover\.ebay\.com|partnerize\.com|howl\.me|geni\.us|"
    r"hop\.clickbank\.net|digistore24\.com|viglink\.com|sovrn\.com|go\.skimresources\.com|"
    r"clk\.tradedoubler\.com|tradedoubler\.com|webgains\.com|impact\.com|pjtra\.com|pjatr\.com|"
    r"emjcd\.com|commission-junction\.com|flexoffers\.com|admitad\.com|ad\.admitad\.com)$", re.I)
PAID_UTM = {"cpc", "ppc", "paid", "affiliate", "display", "sponsored", "ad", "ads", "paidsearch"}
REDIRECT_PATH = re.compile(r"/(go|out|aff|track|click|clk|redirect|redir|rs|visit|ref|r)(/|\?|$)", re.I)
SRC_KEYS = {"src", "source", "via", "agent", "channel", "surface", "s"}

LABEL = re.compile(
    r"is_sponsored\"?\s*:\s*true|\"sponsored\"\s*:\s*(true|\[\s*\{)|is_promoted\"?\s*:\s*true|"
    r"promotion_tier\"?\s*:\s*\"[^\"]+\"|\"promoted\"\s*:\s*true|\[sponsored\]|\(sponsored\)|"
    r"disclosure_label\"?\s*:\s*\"ad\"|\"is_ad\"\s*:\s*true|\"ad\"\s*:\s*true|sponsored via|"
    r"\banzeige\b|\bwerbung\b|\bpaid placement\b|\"sponsored_rank\"\s*:\s*\d|"
    r"<!-- agent-ad(?!-page)|^#+\s*sponsored\b|\"(is_)?featured\"\s*:\s*true|"
    r"\"(tier|placement|listing_type|badge)\"\s*:\s*\"(featured|promoted|sponsored|paid)\"", re.I | re.M)
# a tool whose NAME declares ads (e.g. getMarketplaceAdverts); flagged when it returns a non-empty body
AD_TOOL = re.compile(r"advert|sponsor|promot|(^|_)ads?($|_)|adunit|placement", re.I)
EMPTY = re.compile(r"^\s*(\[\s*\]|\{\s*\}|null|)\s*$")
NEG_LABEL = re.compile(r"is_sponsored\"?\s*:\s*false|\"sponsored\"\s*:\s*(false|\[\s*\])|"
                       r"\"placements\"\s*:\s*\[\s*\]|no paid placement|not sponsored", re.I)
DISCLOSURE = re.compile(r"affiliate link|amazon associate|earns? (a )?commission|may earn|"
                        r"commission[s]? (from|on)|relationship\W+affiliate|sponsored", re.I)


def url_signals(u):
    sp = urlsplit(u)
    host = (sp.hostname or "").lower()
    q = parse_qsl(sp.query, keep_blank_values=True)
    keys = {k.lower() for k, _ in q}
    sig = set()
    if re.search(r"[?&]tag=[A-Za-z0-9_.-]+-2\d\b", u):
        sig.add("aff_param")
    if keys & AFF_KEYS:
        sig.add("aff_param")
    if AFF_NETWORK.search(host):
        sig.add("aff_network")
    for k, v in q:
        if k.lower() == "utm_medium" and v.lower() in PAID_UTM:
            sig.add("paid_utm")
    if any(k.startswith("utm_") for k in keys) and "paid_utm" not in sig:
        sig.add("attrib_utm")
    if REDIRECT_PATH.search(sp.path or ""):
        sig.add("redirect_path")
    if keys & SRC_KEYS:
        sig.add("src_param")
    seg = (sp.path or "/").strip("/").split("/")[0][:30]
    return sig, host, seg, sorted(keys)[:12]


STRONG = {"aff_param", "aff_network", "paid_utm", "label", "ad_tool", "disclosure"}

# recall: affiliate links wrapped inside a redirect (…/c?u=<amazon…tag=…>, /go?to=<awin…>, or a
# base64/JWT path token whose JSON names the destination). Emitted as an extra item of kind
# "nested" so the outer URL's signature (and its id) is unchanged.
NEST_KEYS = {"u", "url", "to", "d", "dest", "destination", "ued", "aff_url", "target", "redirect",
             "link", "r", "out", "goto"}


def inner_urls(u):
    from urllib.parse import unquote
    import base64
    sp = urlsplit(u)
    found = []
    for k, v in parse_qsl(sp.query, keep_blank_values=True):
        if k.lower() in NEST_KEYS:
            v = unquote(v)
            if v.startswith("http"):
                found.append(v)
            else:
                try:
                    b = base64.urlsafe_b64decode(v + "=" * (-len(v) % 4)).decode("utf-8", "ignore")
                    found += re.findall(r"https?://[^\s\"']+", b)
                except ValueError:
                    pass
    for seg in (sp.path or "").split("/"):
        for part in seg.split(".")[:2]:
            if len(part) >= 24:
                try:
                    b = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)).decode("utf-8", "ignore")
                except ValueError:
                    continue
                found += [x.replace("\\/", "/") for x in re.findall(r"https?:(?:\\?/){2}[^\s\"'\\]+", b)]
    return found


def detect_items(r):
    """candidate items of one response r = {rid, run, host, tool, text, ok}; also used by
    analysis/ad_metadata to classify newly probed responses with the same signatures."""
    t = r["text"] or ""
    if not t or not r["ok"]:
        return []
    disc = bool(DISCLOSURE.search(t))
    items = []
    for m in URL.finditer(t):
        u = m.group(0).rstrip(".,;:")
        if IMG.search(urlsplit(u).path or ""):
            continue
        s, host, seg, keys = url_signals(u)
        if s:
            items.append(("url", u, s, host, seg, keys, m.start()))
        for iu in inner_urls(u):
            si, ihost, _, _ = url_signals(iu)
            si &= {"aff_param", "aff_network", "paid_utm"}
            if si:
                items.append(("nested", u, si, host, ihost[:30], [], m.start()))
                break
    for m in LABEL.finditer(t):
        items.append(("label", m.group(0), {"label"}, "", m.group(0).lower()[:24], [], m.start()))
    # response-level kinds (recall: ads carried without a tracked link or item label)
    if AD_TOOL.search(r["tool"] or "") and not EMPTY.match(t):
        items.append(("ad_tool", t[:200], {"ad_tool"}, "", (r["tool"] or "")[:24], [], 0))
    if disc and not any(s & STRONG for _, _, s, *_ in items):
        m = DISCLOSURE.search(t)
        items.append(("disclosure", m.group(0), {"disclosure"}, "", m.group(0).lower()[:24], [],
                      m.start()))
    recs = []
    for kind, val, s, host, seg, keys, pos in items:
        key = (r["host"], r["tool"], kind, ",".join(sorted(s)), host, seg, ",".join(keys))
        sk = hashlib.sha1("|".join(key).encode()).hexdigest()[:12]
        recs.append(({"rid": r["rid"], "run": r["run"], "host": r["host"], "tool": r["tool"],
                      "kind": kind, "value": val[:4000], "signals": sorted(s),
                      "strong": bool(s & STRONG), "url_host": host, "seg": seg,
                      "sig": sk, "resp_disclosure": disc, "neg_label_in_resp": bool(NEG_LABEL.search(t)),
                      "context": re.sub(r"\s+", " ", t[max(0, pos - 300):pos + 300])}, key, s))
    return recs


def main():
    sigs = defaultdict(lambda: {"n_items": 0, "rids": set(), "examples": []})
    n_items = 0
    with open(OUT / "candidates.jsonl", "w") as fo:
        for line in open(OUT / "responses.jsonl"):
            r = json.loads(line)
            for rec, key, s in detect_items(r):
                sk = rec["sig"]
                fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_items += 1
                g = sigs[sk]
                g["key"] = key
                g["n_items"] += 1
                g["rids"].add(r["rid"])
                g["strong"] = bool(s & STRONG)
                g["needs_review"] = bool(s & STRONG) or "redirect_path" in s
                if len(g["examples"]) < 2:
                    g["examples"].append(rec["context"][150:520])
    with open(OUT / "signatures.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sig", "host", "tool", "kind", "signals", "url_host", "seg", "param_keys",
                    "strong", "needs_review", "n_items", "n_responses", "example"])
        for sk, g in sorted(sigs.items(), key=lambda kv: (kv[1]["key"][0], kv[1]["key"][1])):
            w.writerow([sk, *g["key"], g["strong"], g["needs_review"], g["n_items"], len(g["rids"]),
                        g["examples"][0]])
    nr = sum(g["needs_review"] for g in sigs.values())
    print(f"candidate items: {n_items}; signatures: {len(sigs)}; needing review: {nr}; "
          f"hosts needing review: {len({g['key'][0] for g in sigs.values() if g['needs_review']})}")


if __name__ == "__main__":
    main()
