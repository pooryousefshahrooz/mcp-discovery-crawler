#!/usr/bin/env python3
"""S7 - Quantify advertisement origins from the final per-signature codes and draw the figure.

Units (all derived from confirmed_ad signatures in out/final_codes.json)
  ad item       one candidate item (S2) of a confirmed signature
  distinct ad   one ad identity per server: the normalized destination of a URL item (nested
                destination decoded, volatile params such as ts/sig/click ids/utm dropped), or,
                for responses whose ads carry no URL (labels, ad blocks, advert tools), the
                labelled item's surrounding text
  impression    one (response, distinct ad) pair
  path          one (server, tool, origin) combination
Responses with ad items of several origins are counted once per origin.

Stability: in the five-times replicated runs (adtools-r1..5, qbattery-r1..5, fn-r1..5) each
(server, tool, arguments) group is checked for whether ad presence is the same in all reps.

Outputs (out/): ad_items.csv, ad_provenance_results.csv, ad_provenance_summary.json,
                fig_ad_provenance.pdf / .png

  python3 analysis/ad_provenance/s7_quantify.py
"""
import base64
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

ORIGINS = ["operator", "upstream_api", "third_party_content", "multiple", "unknown"]
LABEL = {"operator": "MCP server operator", "upstream_api": "Upstream search/API provider",
         "third_party_content": "Retrieved third-party content", "multiple": "Multiple sources",
         "unknown": "Unknown"}
CATS = [("web_search", "Web search"), ("shopping", "Shopping & deals"),
        ("ad_network", "Ad network"), ("other", "Other vertical")]
VOLATILE = re.compile(r"^(ts|sig|exp|iat|click_uuid|ascsubtag|match_id|clickref|xcust|d|s|src|via|agent|"
                      r"utm_.*|sid|q|loc|source|surface|t|n|serve_id|_gsid|clk.*|id|campaign|sref|"
                      r"product_id|merchant|aff_url|subid.*|sharedid|linkid|ref_|language|th|psc|linkcode|"
                      r"amdata|hash|_skw|mkevt|mkcid|mkrid|toolid|customid|articleorsubsection|asc_.*)$", re.I)
NOT_AD_ITEM = re.compile(r'"(?:affiliate|aff|is_affiliate|is_sponsored|sponsored)"\s*:\s*false', re.I)
REPS = re.compile(r"^full/(adtools|qbattery|fn)-r\d$")


def destination(u):
    """follow one level of nesting (query param or base64 path token) to the real destination."""
    sp = urlsplit(u)
    for k, v in parse_qsl(sp.query):
        if k.lower() in ("u", "url", "to", "ued", "dest", "destination", "target") and unquote(v).startswith("http"):
            return unquote(v)
    for part in re.split(r"[/.]", sp.path or ""):
        if len(part) >= 24:
            try:
                b = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)).decode("utf-8", "ignore")
            except ValueError:
                continue
            m = re.search(r'"(?:u|t|d|dest)"\s*:\s*"(https?:[^"]+)"', b)
            if m:
                return m.group(1).replace("\\/", "/")
    return u


def norm(u):
    d = destination(u)
    sp = urlsplit(d)
    q = sorted((k, v) for k, v in parse_qsl(sp.query) if not VOLATILE.match(k))
    path = re.sub(r"(%7C[^%/]+)%7C[^/]*$", r"\1", sp.path.rstrip("/"), flags=re.I)
    return f"{(sp.hostname or '').lower()}{path}" + (f"?{urlencode(q)}" if q else "")


ITEM_KEY = re.compile(r'creative="([^"]+)"|"(?:title|name|product_name|sponsor|product_id|id)"\s*:\s*"?([^",}]{2,80})'
                      r'|\*\*([^*]{3,80})\*\*')


def rejoin(text, frag):
    """S2's URL pattern stops at '|', which splits links such as Amazon's
    ...&asc_source=|https://page...&tag=x-20 into fragments. Rebuild the whole link: walk back from
    the fragment over non-space characters to the markdown/JSON link start."""
    i = text.find(frag)
    if i <= 0 or text[i - 1] != "|":
        return frag
    j = i
    while j > 0 and not text[j - 1].isspace() and text[j - 1] not in '("[<':
        j -= 1
    k = text.find("http", j, i)
    return text[k:i + len(frag)] if 0 <= k < i else frag


def enclosing_object(text, needle):
    """the innermost JSON object around the first occurrence of needle (brace matching)."""
    i = text.find(needle)
    if i < 0:
        return ""
    depth, a = 0, i
    while a > 0:
        a -= 1
        if text[a] == "}":
            depth += 1
        elif text[a] == "{":
            if depth == 0:
                break
            depth -= 1
    depth, b = 0, i
    while b < len(text):
        if text[b] == "{":
            depth += 1
        elif text[b] == "}":
            if depth == 0:
                break
            depth -= 1
        b += 1
    return text[a:b + 1]


def label_item(ctx):
    """identity of the item a label belongs to: the last item key (title/name/id, ad creative id,
    or markdown bold name) before the label, which sits ~300 chars into the context window."""
    m = re.search(r'creative="([^"]+)"', ctx)
    if m:
        return "item:" + m.group(1)
    keys = [m for m in ITEM_KEY.finditer(ctx[:300]) if not re.search(r"(?i)sponsor|anzeige|promoted", m.group(0))]
    if not keys:
        return "label:" + hashlib.sha1(ctx[150:300].encode()).hexdigest()[:10]
    m = keys[-1]
    return "item:" + next(g for g in m.groups() if g).strip().lower()


def main():
    final = json.load(open(OUT / "final_codes.json"))
    conf = {k: v for k, v in final.items() if v["status"] == "confirmed_ad"}
    sigrow = {s["sig"]: s for s in csv.DictReader(open(OUT / "signatures.csv"))}
    path_cat = {}
    for k, v in conf.items():
        s = sigrow[k]
        if v.get("tool_category"):
            path_cat.setdefault((s["host"], s["tool"]), Counter())[v["tool_category"]] += 1

    # ad identities per response
    by_resp = defaultdict(lambda: {"url": set(), "other": set(), "deferred": False})
    meta = {}
    resp_sigs = defaultdict(set)
    n_flagged_not_ad = Counter()
    url_rids = set()
    for line in open(OUT / "candidates.jsonl"):
        c = json.loads(line)
        if c["sig"] in conf and c["kind"] in ("url", "nested"):
            url_rids.add(c["rid"])
    rtext = {}
    for line in open(OUT / "responses.jsonl"):
        r = json.loads(line)
        if r["rid"] in url_rids:
            rtext[r["rid"]] = r["text"] or ""
    for line in open(OUT / "candidates.jsonl"):
        c = json.loads(line)
        if c["sig"] not in conf:
            continue
        o = conf[c["sig"]]["origin"]
        key = (c["rid"], o)
        meta[c["rid"]] = (c["host"], c["tool"], c["run"])
        resp_sigs[key].add(c["sig"])
        if c["kind"] in ("url", "nested"):
            # the server itself marks this item as not monetized -> not an ad (e.g. wem3 rows
            # with "affiliate": false that still go through the /api/go redirect)
            if NOT_AD_ITEM.search(enclosing_object(rtext.get(c["rid"], ""), c["value"][:200])):
                n_flagged_not_ad[c["host"]] += 1
                continue
            full = rejoin(rtext.get(c["rid"], ""), c["value"])
            by_resp[key]["url"].add((norm(full), full[:300]))
        elif c["kind"] in ("disclosure", "ad_tool"):
            # a disclosure (or an ad-declaring tool) is not itself an ad: the ads are the items the
            # response returns. Count each returned item link; a response with none adds nothing.
            by_resp[key]["deferred"] = True
        else:
            by_resp[key]["other"].add((label_item(c["context"]), c["value"][:120]))

    need = {rid for (rid, _o), d in by_resp.items() if d.get("deferred") and not d["url"] and not d["other"]}
    texts = {}
    if need:
        for line in open(OUT / "responses.jsonl"):
            r = json.loads(line)
            if r["rid"] in need:
                texts[r["rid"]] = r["text"] or ""
    for (rid, o), d in by_resp.items():
        if rid in texts:
            t = texts[rid]
            # returned items: item-level url/link fields, or advert records with a title
            # only link fields of returned ITEMS: innermost JSON objects that also carry a
            # title/name/price (excludes service links such as /extension or a site's /shop root)
            for obj in re.finditer(r"\{[^{}]*\}", t):
                o_ = obj.group(0)
                if not re.search(r'"(?:title|name|Title|price|price_cents|current_price_cents)"\s*:', o_):
                    continue
                for m in re.finditer(r'"(?:url|link|product_url|buy_url|listing_url|URL|Url|Link)"\s*:\s*"(https?://[^"]+)"', o_):
                    if not re.search(r"\.(png|jpe?g|webp|gif|svg)(\?|$)", m.group(1), re.I):
                        d["url"].add((norm(m.group(1)), m.group(1)[:300]))
            if not d["url"]:
                for m in re.finditer(r'"(?:Title|title|name)"\s*:\s*"([^"]{3,120})"', t):
                    d["other"].add(("item:" + m.group(1).lower(), m.group(1)))

    ads = {}            # (host, origin, identity) -> stats
    impressions = Counter()
    resp_origin = defaultdict(set)
    path_stats = defaultdict(lambda: {"impressions": 0, "responses": set(), "ads": set()})
    for (rid, o), d in by_resp.items():
        host, tool, run = meta[rid]
        idents = d["url"] if d["url"] else d["other"]
        if not idents:
            continue
        resp_origin[rid].add(o)
        for ident, example in idents:
            k = (host, o, ident)
            a = ads.setdefault(k, {"server": host, "origin": o, "identity": ident, "example": example,
                                   "tools": set(), "impressions": 0, "runs": set(), "sigs": set()})
            a["tools"].add(tool); a["impressions"] += 1; a["runs"].add(run); a["sigs"] |= resp_sigs[(rid, o)]
            impressions[o] += 1
            ps = path_stats[(host, tool, o)]
            ps["impressions"] += 1; ps["responses"].add(rid); ps["ads"].add(ident)

    def cat_of(host, tool):
        c = path_cat.get((host, tool))
        return c.most_common(1)[0][0] if c else "other"

    # stability across replicated runs
    calls = defaultdict(dict)
    ad_rids = set(meta)
    paths = {(h, t) for (h, t, _o) in path_stats}
    for line in open(OUT / "responses.jsonl"):
        r = json.loads(line)
        if not REPS.match(r["run"]) or (r["host"], r["tool"]) not in paths or not r["ok"]:
            continue
        fam = r["run"].split("/")[1].split("-")[0]
        g = (r["host"], r["tool"], fam, json.dumps(r["arguments"], sort_keys=True))
        calls[g][r["run"]] = calls[g].get(r["run"], False) or (r["rid"] in ad_rids)
    groups = [v for v in calls.values() if len(v) >= 3]
    consistent = sum(len(set(v.values())) == 1 for v in groups)

    # outputs
    with open(OUT / "ad_items.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["server", "origin", "identity", "tools", "impressions", "n_runs", "signatures", "example"])
        for a in sorted(ads.values(), key=lambda a: (a["server"], -a["impressions"])):
            w.writerow([a["server"], a["origin"], a["identity"], ";".join(sorted(a["tools"])), a["impressions"],
                        len(a["runs"]), ";".join(sorted(a["sigs"])), a["example"]])

    sig_by_path = defaultdict(list)
    for k, v in conf.items():
        s = sigrow[k]
        sig_by_path[(s["host"], s["tool"], v["origin"])].append((k, v))
    conf_rank = {"high": 3, "medium": 2, "low": 1}
    rows = []
    for (h, t, o), ps in sorted(path_stats.items()):
        sv = sig_by_path[(h, t, o)]
        best = max(sv, key=lambda kv: conf_rank.get(kv[1]["confidence"], 0))[1]
        rows.append({"server": h, "tool": t, "tool_category": cat_of(h, t), "origin": o,
                     "confidence": best["confidence"], "basis": best["basis"],
                     "distinct_ads": len(ps["ads"]), "impressions": ps["impressions"],
                     "ad_responses": len(ps["responses"]),
                     "signatures": ";".join(k for k, _ in sv),
                     "evidence": " || ".join(sorted({v["note"] for _, v in sv}))[:900],
                     "verification": " || ".join(sorted({v.get("verification", "") for _, v in sv} - {""}))[:900],
                     "decided_by": ";".join(sorted({v["decided_by"] for _, v in sv}))})
    with open(OUT / "ad_provenance_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    def block(sel_rows, sel_ads, sel_imp):
        n_ads = len(sel_ads)
        return {
            "distinct_ads": {o: sum(a["origin"] == o for a in sel_ads) for o in ORIGINS},
            "distinct_ads_n": n_ads,
            "impressions": {o: sel_imp.get(o, 0) for o in ORIGINS},
            "impressions_n": sum(sel_imp.values()),
            "paths": {o: sum(r["origin"] == o for r in sel_rows) for o in ORIGINS},
            "paths_n": len(sel_rows),
            "servers": {o: len({r["server"] for r in sel_rows if r["origin"] == o}) for o in ORIGINS},
            "servers_n": len({r["server"] for r in sel_rows}),
        }

    ad_list = list(ads.values())
    S = {"overall": block(rows, ad_list, impressions)}
    S["items_server_flagged_not_ad"] = dict(n_flagged_not_ad)
    S["ad_responses"] = len(resp_origin)
    S["ad_responses_mixed_origin"] = sum(len(v) > 1 for v in resp_origin.values())
    by_cat = {}
    for key, _lab in CATS:
        pr = [r for r in rows if r["tool_category"] == key]
        pa = [a for a in ad_list if any(cat_of(a["server"], t) == key for t in a["tools"])]
        pi = Counter()
        for (h, t, o), ps in path_stats.items():
            if cat_of(h, t) == key:
                pi[o] += ps["impressions"]
        by_cat[key] = block(pr, pa, pi)
    S["by_category"] = by_cat
    n = len(ad_list)
    conf_of_ad = {}
    for a in ad_list:
        # an ad is as well attributed as the best signature that actually carried it
        conf_of_ad[(a["server"], a["identity"])] = max((conf_rank.get(conf[k]["confidence"], 0)
                                                        for k in a["sigs"]), default=0)
    S["verifiable_pct_ads"] = round(100 * sum(a["origin"] != "unknown" for a in ad_list) / n, 1)
    S["high_conf_pct_ads"] = round(100 * sum(conf_of_ad[(a["server"], a["identity"])] == 3
                                             and a["origin"] != "unknown" for a in ad_list) / n, 1)
    S["confidence_ads"] = dict(Counter({3: "high", 2: "medium", 1: "low", 0: "n/a"}[v] for v in conf_of_ad.values()))
    S["basis_paths"] = dict(Counter(r["basis"] for r in rows))
    S["stability"] = {"replicated_groups": len(groups), "consistent_presence": consistent,
                      "consistent_pct": round(100 * consistent / len(groups), 1) if groups else None}
    st = Counter(v["status"] for v in final.values())
    S["signature_status"] = dict(st)
    S["servers_by_status"] = {k: len({sigrow[s]["host"] for s, v in final.items() if v["status"] == k})
                              for k in st}
    json.dump(S, open(OUT / "ad_provenance_summary.json", "w"), indent=1)
    figure(S)
    print(json.dumps({k: S[k] for k in ("overall", "verifiable_pct_ads", "high_conf_pct_ads",
                                        "confidence_ads", "stability", "servers_by_status")}, indent=1))


def figure(S):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.family": "sans-serif",
                         "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"], "font.size": 7.5,
                         "axes.linewidth": 0.6, "axes.edgecolor": "#52514e", "xtick.color": "#52514e",
                         "ytick.color": "#0b0b0b", "xtick.major.width": 0.6, "ytick.major.size": 0})
    COL = {"operator": "#2a78d6", "third_party_content": "#eb6834", "upstream_api": "#1baf7a",
           "multiple": "#eda100", "unknown": "#a3a29c"}
    HATCH = {"unknown": "////"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.3), gridspec_kw={"width_ratios": [1, 1]})
    fig.patch.set_facecolor("white")

    def stack(ax, labels, items):
        for i, (b, unit) in enumerate(items):
            n = b[unit + "_n"]
            left = 0.0
            for o in ORIGINS:
                w = 100 * b[unit][o] / n if n else 0
                if w <= 0:
                    continue
                ax.barh(i, w, left=left, height=0.62, color=COL[o], hatch=HATCH.get(o),
                        edgecolor="white", linewidth=1.0)
                if w >= 12:
                    ax.text(left + w / 2, i, f"{w:.1f}%" if 99 < w < 100 else f"{w:.0f}%", ha="center", va="center", fontsize=7,
                            color="white" if o not in ("unknown", "multiple") else "#0b0b0b")
                left += w
        ax.set_yticks(range(len(labels)), labels)
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100%"])
        ax.grid(axis="x", color="#e4e3df", linewidth=0.5)
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)

    o = S["overall"]
    stack(ax1, [f"Distinct ads\n(n={o['distinct_ads_n']})", f"Ad impressions\n(n={o['impressions_n']})",
                f"Ad-serving tools\n(n={o['paths_n']}; {o['servers_n']} servers)"],
          [(o, "distinct_ads"), (o, "impressions"), (o, "paths")])
    ax1.set_title("(a) Origin of advertisements", fontsize=8, loc="left", fontweight="bold")

    cats = [(k, lab) for k, lab in CATS if S["by_category"][k]["distinct_ads_n"]]
    stack(ax2, [f"{lab}\n(n={S['by_category'][k]['distinct_ads_n']} ads; "
                f"{S['by_category'][k]['servers_n']} srv)" for k, lab in cats],
          [(S["by_category"][k], "distinct_ads") for k, _ in cats])
    ax2.set_title("(b) Origin by tool category (distinct ads)", fontsize=8, loc="left", fontweight="bold")

    handles = [Patch(visible=False, label="Distinct ads:")] + [
        Patch(facecolor=COL[k], hatch=HATCH.get(k), edgecolor="white",
              label=f"{LABEL[k]} ({o['distinct_ads'][k]})") for k in ORIGINS]
    fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False, fontsize=7,
               handlelength=1.4, columnspacing=1.1, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.09, 1, 1), w_pad=2.0)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_ad_provenance.{ext}", dpi=300, facecolor="white", bbox_inches="tight")


if __name__ == "__main__":
    main()
