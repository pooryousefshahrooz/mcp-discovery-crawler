#!/usr/bin/env python3
"""S8 - How much do the headline numbers depend on weaker evidence and counting choices?

Recomputes the operator share of distinct ads and the server count under:
  all                      final codes as reported
  high_conf_only           only ads carried by a high-confidence signature
  no_documentation_only    drop paths whose best evidence is the operator's own statement
  no_single_coder          drop signatures decided by one coder only
  wo_family_as_one         the 14 wo*.de price-comparison sites (identical tool, instructions and
                           affiliate IDs) counted as one server — a counting choice, not an
                           ownership claim
and reports concentration (share of distinct ads from the top 3 / top 5 servers), plus three
facts used in the paper text:
  disclosure_location      for ads whose attribution rests only on documentation: is an explicit
                           affiliate/sponsored statement inside the ad-bearing response itself, or
                           only in tool descriptions / server instructions?
  probe_allocation         share of calls (and of ad servers) belonging to servers whose metadata
                           declares paid content (analysis/ads_labels_full.json, neutrality excluded)
  web_search_tools         general web-search tools that returned results, and how often called

  python3 analysis/ad_provenance/s8_sensitivity.py  -> out/sensitivity.json
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"


def main():
    final = json.load(open(OUT / "final_codes.json"))
    paths = list(csv.DictReader(open(OUT / "ad_provenance_results.csv")))
    ads = list(csv.DictReader(open(OUT / "ad_items.csv")))
    sig_of_path = {(p["server"], p["tool"], p["origin"]): p["signatures"].split(";") for p in paths}

    def stats(sel):
        n = len(sel)
        op = sum(a["origin"] == "operator" for a in sel)
        servers = {a["server"] for a in sel}
        op_srv = {a["server"] for a in sel if a["origin"] == "operator"}
        return {"distinct_ads": n, "operator_pct": round(100 * op / n, 1) if n else None,
                "servers": len(servers), "operator_servers": len(op_srv),
                "non_operator_ads": n - op}

    out = {"all": stats(ads)}
    # per ad: the signatures that actually carried it (same rule as s7)
    sigs = {(a["server"], a["identity"]): [k for k in a["signatures"].split(";") if k in final] for a in ads}
    out["high_conf_only"] = stats([a for a in ads if any(
        final[k]["confidence"] == "high" for k in sigs[(a["server"], a["identity"])])])
    doc_only = [a for a in ads if all(final[k]["basis"] == "documentation" for k in sigs[(a["server"], a["identity"])])]
    out["no_documentation_only"] = stats([a for a in ads if a not in doc_only])
    single = {k for k, v in final.items() if v["decided_by"] == "single_coder"}
    out["no_single_coder"] = stats([a for a in ads if not set(
        s for t in a["tools"].split(";") for s in sig_of_path.get((a["server"], t, a["origin"]), [])) <= single])
    wo = re.compile(r"^wo[a-z]+\.de$")
    fam = [dict(a, server="wo*.de" if wo.match(a["server"]) else a["server"]) for a in ads]
    out["wo_family_as_one"] = stats(fam)
    c = Counter(a["server"] for a in ads)
    n = len(ads)
    out["concentration"] = {"top3": [h for h, _ in c.most_common(3)],
                            "top3_pct": round(100 * sum(v for _, v in c.most_common(3)) / n, 1),
                            "top5_pct": round(100 * sum(v for _, v in c.most_common(5)) / n, 1),
                            "median_ads_per_server": sorted(c.values())[len(c) // 2]}
    out["documentation_only_ads"] = {"ads": len(doc_only), "pct": round(100 * len(doc_only) / n, 1),
                                     "servers": len({a["server"] for a in doc_only})}

    # disclosure location for documentation-only ads: an explicit statement (not a field name or a
    # URL parameter) inside an AD-BEARING response of that server
    STMT = re.compile(r"affiliate[- ]links?|affiliate-tracked|amazon associate|earns? from qualifying|"
                      r"(may|might|can) (earn|receive)|earns? (a |affiliate )?commission|commission (goes|from)|"
                      r"relationship: affiliate|kann affiliate|affiliate partner|la commissione|"
                      r"\(sponsored\)|\[sponsored\]|sponsored via|affiliate\)", re.I)
    conf_sigs = {k for k, v in final.items() if v["status"] == "confirmed_ad"}
    doc_servers = {a["server"] for a in doc_only}
    ad_rids = set()
    for line in open(OUT / "candidates.jsonl"):
        c_ = json.loads(line)
        if c_["sig"] in conf_sigs and c_["host"] in doc_servers:
            ad_rids.add(c_["rid"])
    resp_disc = {}
    for line in open(OUT / "responses.jsonl"):
        r = json.loads(line)
        if r["rid"] in ad_rids:
            t = re.sub(r"https?://\S+", " ", r["text"] or "")
            t = re.sub(r'"[A-Za-z_]+"\s*:', " ", t)
            if STMT.search(t):
                resp_disc[r["host"]] = True
    inresp = [a for a in doc_only if resp_disc.get(a["server"])]
    out["disclosure_location"] = {
        "doc_only_ads": len(doc_only),
        "statement_in_response_ads": len(inresp),
        "statement_in_response_servers": len({a["server"] for a in inresp}),
        "only_in_descriptions_or_instructions_ads": len(doc_only) - len(inresp),
        "only_in_descriptions_or_instructions_servers": sorted(doc_servers - {a["server"] for a in inresp})}

    # probe allocation: calls to servers whose metadata declares paid content
    from urllib.parse import urlsplit
    labels = json.load(open(OUT.parents[1] / "ads_labels_full.json"))
    declared = {urlsplit(u).hostname for k, v in labels.items() if k != "neutrality_claim" for u in v}
    calls, hosts = Counter(), set()
    for line in open(OUT / "responses.jsonl"):
        r = json.loads(line)
        calls[r["host"] in declared] += 1
        hosts.add(r["host"])
    ad_servers = {a["server"] for a in ads}
    out["probe_allocation"] = {
        "declared_hosts_probed": len(hosts & declared), "hosts_probed": len(hosts),
        "calls_to_declared": calls[True], "calls_total": sum(calls.values()),
        "calls_to_declared_pct": round(100 * calls[True] / sum(calls.values()), 1),
        "ad_servers_declared": len(ad_servers & declared), "ad_servers": len(ad_servers),
        "ad_servers_not_declared": sorted(ad_servers - declared)}

    # general web-search tools
    WS = re.compile(r"web_?search|search_?web|internet_search|google_search|bing|brave_search|tavily|"
                    r"serp|firecrawl_search|exa_search|perplexity|duckduckgo|websearch", re.I)
    ws = Counter()
    for line in open(OUT / "responses.jsonl"):
        r = json.loads(line)
        if WS.search(r["tool"] or "") and r["ok"] and r["text"]:
            ws[(r["host"], r["tool"])] += 1
    out["web_search_tools"] = {"tools_returning_results": len(ws), "successful_calls": sum(ws.values()),
                               "tools": {f"{h}::{t}": n for (h, t), n in sorted(ws.items())}}
    json.dump(out, open(OUT / "sensitivity.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
