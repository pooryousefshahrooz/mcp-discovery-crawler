#!/usr/bin/env python3
"""S6 - Inter-coder agreement, adjudication, and the final per-signature codes.

Inputs
  out/coding_A.json, out/coding_B.json   two independent codings of the review sheets
  coding/adjudication.json               adjudicated decision for every A/B disagreement
  coding/verification.json               post-hoc code / upstream evidence (applied last)
  out/signatures.csv                     all signatures (incl. attribution-only)

Steps
  1. agreement on signatures both coders coded: status (4-way), confirmed yes/no, and
     origin on signatures both coded confirmed_ad; Cohen's kappa for each
  2. disagreements -> out/disagreements.csv (adjudication must cover every one)
  3. final code = agreed code, or the adjudicated code where A and B differ
  4. attribution-only signatures not flagged by either coder get the codebook default
     (promotional/operator: UTM/src attribution on links the server returns); coders flagged
     the exceptions (third-party pages' own UTMs -> not_ad, hidden ads -> confirmed_ad)
  5. verification evidence overrides basis/confidence/status where code was inspected
  -> out/final_codes.json, out/agreement.json

  python3 analysis/ad_provenance/s6_adjudicate.py
"""
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"


def kappa(pairs):
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


def main():
    A = json.load(open(OUT / "coding_A.json"))
    B = json.load(open(OUT / "coding_B.json"))
    sigs = {s["sig"]: s for s in csv.DictReader(open(OUT / "signatures.csv"))}
    review = {k for k, s in sigs.items() if s["needs_review"] == "True"}

    both = sorted((set(A) & set(B)) & set(sigs))
    st = [(A[k]["status"], B[k]["status"]) for k in both]
    conf = [(A[k]["status"] == "confirmed_ad", B[k]["status"] == "confirmed_ad") for k in both]
    oc = [k for k in both if A[k]["status"] == B[k]["status"] == "confirmed_ad"]
    org = [(A[k]["origin"], B[k]["origin"]) for k in oc]
    agr = {
        "n_review_signatures": len(review), "coded_by_both": len(both),
        "missing_in_B": sorted(review - set(B)), "missing_in_A": sorted(review - set(A)),
        "status_agreement": round(sum(a == b for a, b in st) / len(st), 3), "status_kappa": kappa(st),
        "confirmed_agreement": round(sum(a == b for a, b in conf) / len(conf), 3),
        "confirmed_kappa": kappa(conf),
        "origin_n": len(org), "origin_agreement": round(sum(a == b for a, b in org) / len(org), 3) if org else None,
        "origin_kappa": kappa(org),
    }
    dis = [k for k in both if (A[k]["status"], A[k]["origin"]) != (B[k]["status"], B[k]["origin"])]
    with open(OUT / "disagreements.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sig", "host", "tool", "A_status", "A_origin", "A_note", "B_status", "B_origin", "B_note"])
        for k in dis:
            s = sigs[k]
            w.writerow([k, s["host"], s["tool"], A[k]["status"], A[k]["origin"], A[k]["note"],
                        B[k]["status"], B[k]["origin"], B[k].get("note", "")])
    agr["n_disagreements"] = len(dis)

    adj_path = HERE / "coding" / "adjudication.json"
    adj = json.load(open(adj_path)) if adj_path.exists() else {}
    adj = {k: v for k, v in adj.items() if not k.startswith("_")}
    missing = [k for k in dis if k not in adj]
    agr["unadjudicated"] = missing

    final = {}
    for k in review | (set(A) | set(B)):
        if k not in sigs:
            continue
        if k in adj:
            c = dict(adj[k]); c["decided_by"] = "adjudication"
        elif k in A and k in B:
            c = dict(A[k]); c["decided_by"] = "agreement"
            c["note_B"] = B[k].get("note", "")
        else:  # coded by one coder only (attribution-only exception) -> needs adjudication too
            c = dict(adj.get(k) or A.get(k) or B.get(k)); c["decided_by"] = "single_coder"
        final[k] = c

    # attribution-only default (codebook): promotional / operator
    for k, s_ in sigs.items():
        if k not in final:
            final[k] = {"status": "promotional", "origin": "operator", "basis": "in_response_trace",
                        "confidence": "medium", "tool_category": "", "note": "attribution-only default (codebook)",
                        "decided_by": "default_rule"}

    ver = json.load(open(HERE / "coding" / "verification.json"))["evidence"]
    for k, v in ver.items():
        if k in final:
            final[k].update(v["set"])
            final[k]["verification"] = v["ref"]

    json.dump(final, open(OUT / "final_codes.json", "w"), indent=1)
    json.dump(agr, open(OUT / "agreement.json", "w"), indent=1)
    print(json.dumps(agr, indent=1))
    print(f"final codes: {len(final)} signatures ({Counter(c['decided_by'] for c in final.values())})")


if __name__ == "__main__":
    main()
