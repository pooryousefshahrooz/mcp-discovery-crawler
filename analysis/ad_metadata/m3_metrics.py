#!/usr/bin/env python3
"""M3 - Apply the hand review to M2's findings and compute every metric.

Inputs : out/responses.jsonl (M1), out/findings.jsonl (M2), coding/field_review.json,
         coding/applicability.json, ad_provenance origins (+ EXTRA hosts of meta_build_plan)
Units  : an AD-CONTAINING response (M1) is the denominator for every exposure rate.
         A category is EXPOSED in a response if >=1 accepted finding of that category is in it.
         `explicit` counts explicit findings only; `any` adds inferred ones.
         N/A (coding/applicability.json) is distinct from 0% (applicable but not observed).
         Servers with no ad-containing response are reported but have no rates (denominator 0).

Outputs (out/):
  findings_accepted.csv           every accepted finding with its exact excerpt
  exposure_by_server_category.csv server x category: n_ad, n_explicit, n_any, rates, N/A, locations
  server_summary.csv              per server: calls, ok, ad-containing, categories exposed, origin
  category_prevalence.csv         per category: servers exposing it / eligible servers
  tool_category_comparison.csv    web search vs shopping vs ad network vs other vertical
  location_by_category.csv        where each category appears (json_field / text / url_param / protocol_meta)
  evidence_examples.csv           one verbatim excerpt per (server, category, basis)
  metrics_summary.json            headline numbers incl. auction-specific exposure

  python3 analysis/ad_metadata/m3_metrics.py
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "out"
CODING = HERE / "coding"
sys.path.insert(0, str(ROOT / "ad_probe"))
from meta_build_plan import EXTRA  # noqa: E402

CATS = ["disclosure", "advertiser", "campaign", "bid", "score", "competing", "winner", "tracking"]
AUCTION = ["bid", "score", "competing", "winner"]
CAT_LABEL = {"disclosure": "Ad disclosure", "advertiser": "Advertiser identity", "campaign": "Campaign ID",
             "bid": "Bid amount", "score": "Auction/ranking score", "competing": "No. competing campaigns",
             "winner": "Winning campaign ID", "tracking": "Affiliate/tracking ID"}
TOOLCAT = {"web_search": "search", "shopping": "shopping", "ad_network": "ad network", "other": "other vertical"}


def load_review():
    rv = json.load(open(CODING / "field_review.json"))
    return rv["reject"], {k: tuple(v) for k, v in rv["remap"].items()}


def decide(f, reject, remap):
    for k in (f"{f['host']}|{f['rule']}", f"*|{f['rule']}"):
        if k in reject:
            return None, reject[k]
        if k in remap:
            f = dict(f, category=remap[k][0], subtype=remap[k][1])
            return f, "remapped"
    if f["category"] == "protocol_header":
        return None, "unmapped header"
    return f, "accepted"


def origins():
    o = defaultdict(Counter)
    for r in csv.DictReader(open(ROOT / "analysis" / "ad_provenance" / "out" / "ad_provenance_results.csv")):
        o[r["server"]][r["origin"]] += 1
    for h, (_e, _c, orig) in EXTRA.items():
        o[h][orig] += 1
    return {h: c.most_common(1)[0][0] for h, c in o.items()}


def main():
    reject, remap = load_review()
    app = json.load(open(CODING / "applicability.json"))
    na = {(h, c) for h in app["servers"] for c in app["na_categories"]}
    origin = origins()

    resp, calls = {}, Counter()
    ok, adr = Counter(), Counter()
    for line in open(OUT / "responses.jsonl"):
        r = json.loads(line)
        calls[r["host"]] += 1
        ok[r["host"]] += r["ok"]
        if r["ad_containing"]:
            adr[r["host"]] += 1
            resp[r["rid"]] = {"host": r["host"], "tool": r["tool"], "tool_category": r["tool_category"],
                              "called_at": r["called_at"], "arguments": r["arguments"]}

    exp = defaultdict(lambda: defaultdict(lambda: {"explicit": False, "any": False}))   # rid -> cat -> flags
    supp = defaultdict(set)                                                             # rid -> x_* cats
    locs = defaultdict(Counter)            # (host, cat) -> location counts (per response)
    comps = defaultdict(Counter)
    examples, review_log = {}, Counter()
    with open(OUT / "findings_accepted.csv", "w", newline="") as fa:
        w = csv.writer(fa)
        w.writerow(["rid", "host", "tool", "tool_category", "category", "subtype", "basis", "location", "component",
                    "path", "rule", "value", "excerpt", "origin_of_ad"])
        seen_loc = set()
        for line in open(OUT / "findings.jsonl"):
            f = json.loads(line)
            if f["rid"] not in resp:
                continue
            f, why = decide(f, reject, remap)
            review_log[why] += 1
            if f is None:
                continue
            c = f["category"]
            # third-party retrieval: identifiers in retrieved pages belong to the page's publisher
            orig = origin.get(f["host"], "operator")
            w.writerow([f["rid"], f["host"], f["tool"], f["tool_category"], c, f["subtype"], f["basis"],
                        f["location"], f["component"], f["path"], f["rule"], f["value"], f["excerpt"], orig])
            if c.startswith("x_"):
                supp[f["rid"]].add(c)
                key = (f["host"], c, f["basis"])
                examples.setdefault(key, f)
                continue
            e = exp[f["rid"]][c]
            e["any"] = True
            e["explicit"] |= f["basis"] == "explicit"
            if (f["rid"], c, f["location"]) not in seen_loc:
                seen_loc.add((f["rid"], c, f["location"]))
                locs[(f["host"], c)][f["location"]] += 1
            if (f["rid"], c, f["component"]) not in seen_loc:
                seen_loc.add((f["rid"], c, f["component"]))
                comps[(f["host"], c)][f["component"]] += 1
            key = (f["host"], c, f["basis"])
            if key not in examples or (len(f["excerpt"]) > len(examples[key]["excerpt"]) and
                                       len(examples[key]["excerpt"]) < 40):
                examples[key] = dict(f, called_at=resp[f["rid"]]["called_at"])

    hosts = sorted(calls)
    analyzed = [h for h in hosts if adr[h] > 0]

    # ---- server x category ----
    cell = {}
    for h in hosts:
        rids = [rid for rid, v in resp.items() if v["host"] == h]
        for c in CATS:
            ne = sum(exp[rid][c]["explicit"] for rid in rids if c in exp[rid])
            nn = sum(exp[rid][c]["any"] for rid in rids if c in exp[rid])
            cell[(h, c)] = {"n_ad": adr[h], "n_explicit": ne, "n_any": nn, "na": (h, c) in na}
    with open(OUT / "exposure_by_server_category.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["server", "category", "n_ad_responses", "applicable", "n_explicit", "n_any",
                    "rate_explicit_pct", "rate_any_pct", "status", "locations", "components"])
        for h in hosts:
            for c in CATS:
                x = cell[(h, c)]
                if x["na"]:
                    st = "not_applicable"
                elif x["n_ad"] == 0:
                    st = "no_ad_responses"
                elif x["n_any"] == 0:
                    st = "not_observed"
                elif x["n_explicit"] == 0:
                    st = "inferred_only"
                else:
                    st = "explicit"
                re_ = round(100 * x["n_explicit"] / x["n_ad"], 1) if x["n_ad"] and not x["na"] else ""
                ra = round(100 * x["n_any"] / x["n_ad"], 1) if x["n_ad"] and not x["na"] else ""
                w.writerow([h, c, x["n_ad"], not x["na"], x["n_explicit"], x["n_any"], re_, ra, st,
                            ";".join(f"{k}:{v}" for k, v in locs[(h, c)].most_common()),
                            ";".join(f"{k}:{v}" for k, v in comps[(h, c)].most_common())])

    # ---- server summary ----
    tc_of = defaultdict(Counter)
    for v in resp.values():
        tc_of[v["host"]][v["tool_category"]] += 1
    plan = json.load(open(ROOT / "ad_probe" / "plan_meta.json"))
    planned = Counter(p["host"] for p in plan)
    stopped = set()
    for h in hosts:
        p = ROOT / "ad_probe" / "results" / "meta_2026-11" / "calls" / f"{h}.jsonl"
        if any(json.loads(l).get("http_status") == 429 for l in open(p)):
            stopped.add(h)
    rows = []
    for h in hosts:
        ce = [c for c in CATS if cell[(h, c)]["n_explicit"]]
        ca = [c for c in CATS if cell[(h, c)]["n_any"]]
        rows.append({"server": h, "planned_calls": planned[h], "calls": calls[h], "ok_responses": ok[h],
                     "ad_containing": adr[h], "stopped_429": h in stopped,
                     "tool_category": (tc_of[h].most_common(1)[0][0] if tc_of[h] else
                                       next(p["tool_category"] for p in plan if p["host"] == h)),
                     "ad_origin": origin.get(h, ""), "n_cats_explicit": len(ce), "n_cats_any": len(ca),
                     "cats_explicit": ";".join(ce), "cats_any": ";".join(ca),
                     "auction_specific_explicit": ";".join(c for c in AUCTION if c in ce),
                     "na_categories": ";".join(c for c in CATS if cell[(h, c)]["na"])})
    with open(OUT / "server_summary.csv", "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # ---- prevalence across servers ----
    prev = []
    for c in CATS:
        elig = [h for h in analyzed if not cell[(h, c)]["na"]]
        se = [h for h in elig if cell[(h, c)]["n_explicit"]]
        sa = [h for h in elig if cell[(h, c)]["n_any"]]
        prev.append({"category": c, "label": CAT_LABEL[c], "eligible_servers": len(elig),
                     "na_servers": len(analyzed) - len(elig),
                     "servers_explicit": len(se), "pct_explicit": round(100 * len(se) / len(elig), 1),
                     "servers_any": len(sa), "pct_any": round(100 * len(sa) / len(elig), 1),
                     "servers_inferred_only": ";".join(sorted(set(sa) - set(se))),
                     "servers": ";".join(sorted(sa))})
    with open(OUT / "category_prevalence.csv", "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(prev[0]))
        w.writeheader()
        w.writerows(prev)

    # ---- tool-category comparison (response level, pooled) ----
    tcr = defaultdict(list)
    for rid, v in resp.items():
        tcr[v["tool_category"]].append(rid)
    tcrows = []
    for tc, rids in sorted(tcr.items()):
        srv = {resp[r]["host"] for r in rids}
        row = {"tool_category": TOOLCAT.get(tc, tc), "servers": len(srv), "ad_responses": len(rids)}
        for c in CATS:
            row[f"{c}_pct_explicit"] = round(100 * sum(exp[r][c]["explicit"] for r in rids if c in exp[r]) / len(rids), 1)
            row[f"{c}_servers_any"] = len({resp[r]["host"] for r in rids if c in exp[r] and exp[r][c]["any"]})
        row["mean_cats_any_per_server"] = round(sum(
            next(x["n_cats_any"] for x in rows if x["server"] == h) for h in srv) / len(srv), 2)
        tcrows.append(row)
    with open(OUT / "tool_category_comparison.csv", "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(tcrows[0]))
        w.writeheader()
        w.writerows(tcrows)

    # ---- locations ----
    with open(OUT / "location_by_category.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["category", "location", "servers", "ad_responses", "component", "servers_c", "ad_responses_c"])
        for c in CATS:
            lc, ls = Counter(), defaultdict(set)
            for (h, cc), cnt in locs.items():
                if cc == c:
                    for k, v in cnt.items():
                        lc[k] += v
                        ls[k].add(h)
            cc_, cs = Counter(), defaultdict(set)
            for (h, cc), cnt in comps.items():
                if cc == c:
                    for k, v in cnt.items():
                        cc_[k] += v
                        cs[k].add(h)
            keys = sorted(set(lc) | set(cc_))
            for k in sorted(lc):
                w.writerow([c, k, len(ls[k]), lc[k], "", "", ""])
            for k in sorted(cc_):
                w.writerow([c, "", "", "", k, len(cs[k]), cc_[k]])

    # ---- evidence ----
    with open(OUT / "evidence_examples.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["server", "category", "basis", "subtype", "location", "component", "path", "value",
                    "excerpt", "rid", "called_at", "ad_origin"])
        for (h, c, b), f in sorted(examples.items()):
            w.writerow([h, c, b, f["subtype"], f["location"], f["component"], f["path"], f["value"],
                        f["excerpt"], f["rid"], f.get("called_at", ""), origin.get(h, "")])

    # ---- headline numbers ----
    nresp = len(resp)
    auc_e = [r for r in resp if any(exp[r][c]["explicit"] for c in AUCTION if c in exp[r])]
    auc_a = [r for r in resp if any(exp[r][c]["any"] for c in AUCTION if c in exp[r])]
    auc_broad = [r for r in resp if r in auc_a or "x_auction_token" in supp[r]]
    app_resp = [r for r in resp if not all((resp[r]["host"], c) in na for c in AUCTION)]
    summ = {
        "eligible_servers": len(hosts) + 2, "probed_servers": len(hosts), "unavailable_servers": 2,
        "calls": sum(calls.values()), "ok_responses": sum(ok.values()), "ad_containing_responses": nresp,
        "servers_with_ad_responses": len(analyzed),
        "servers_without_ad_responses": sorted(set(hosts) - set(analyzed)),
        "servers_stopped_429": sorted(stopped),
        "review": dict(review_log),
        "auction_specific": {
            "responses_explicit": len(auc_e), "responses_any": len(auc_a), "responses_broad_incl_auction_tokens": len(auc_broad),
            "pct_of_ad_responses_explicit": round(100 * len(auc_e) / nresp, 2),
            "pct_of_ad_responses_any": round(100 * len(auc_a) / nresp, 2),
            "pct_of_ad_responses_broad": round(100 * len(auc_broad) / nresp, 2),
            "pct_of_applicable_ad_responses_explicit": round(100 * len(auc_e) / len(app_resp), 2),
            "applicable_ad_responses": len(app_resp),
            "servers_explicit": sorted({resp[r]["host"] for r in auc_e}),
            "servers_any": sorted({resp[r]["host"] for r in auc_a}),
            "servers_broad": sorted({resp[r]["host"] for r in auc_broad}),
            "servers_all_four_explicit": sorted(h for h in analyzed if all(cell[(h, c)]["n_explicit"] for c in AUCTION)),
        },
        "categories_per_server_any": dict(sorted(Counter(x["n_cats_any"] for x in rows if x["ad_containing"]).items())),
        "categories_per_server_explicit": dict(sorted(Counter(x["n_cats_explicit"] for x in rows if x["ad_containing"]).items())),
        "supplementary_servers": {k: sorted({resp[r]["host"] for r in resp if k in supp[r]})
                                  for k in ("x_commission", "x_auction_token", "x_relevance_score")},
    }
    json.dump(summ, open(OUT / "metrics_summary.json", "w"), indent=1)
    print(json.dumps({k: summ[k] for k in ("calls", "ad_containing_responses", "servers_with_ad_responses",
                                           "review", "auction_specific")}, indent=1))
    for p in prev:
        print(f"  {p['label']:26} {p['servers_explicit']:3}/{p['eligible_servers']:<3} explicit  "
              f"{p['servers_any']:3} any   inferred-only: {p['servers_inferred_only']}")


if __name__ == "__main__":
    main()
