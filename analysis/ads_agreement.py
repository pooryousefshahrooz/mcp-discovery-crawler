#!/usr/bin/env python3
"""Compare coder 1 (ads_labels.json) with coder 2 (out/coder2_codes.json):
percent agreement and Cohen's kappa, on the 8-way code and on the binary
'paid influence yes/no' question. Writes out/disagreements.jsonl."""
import argparse, collections, csv, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
MAP = {"ad_network": "AD_NETWORK", "sponsored_in_results": "SPONSORED_RESULTS",
       "affiliate_links_in_results": "AFFILIATE", "agent_paid_to_recommend": "AGENT_PAID_TO_RECOMMEND",
       "neutrality_claim": "NEUTRALITY_CLAIM", "sponsored_content_network": "SPONSORED_CONTENT_NETWORK",
       "competitor_suppression": "COMPETITOR_SUPPRESSION"}
c1 = {e: MAP[k] for k, v in json.load(open(HERE / "ads_labels.json")).items() for e in v}
sheet = [json.loads(l) for l in open(HERE / "out" / "coding_sheet.jsonl")]
ap = argparse.ArgumentParser()
ap.add_argument("--csv", help="a coding_sheet.csv filled in by a human coder (columns code, note)")
args = ap.parse_args()
if args.csv:
    c2 = {r["id"]: [(r["code"] or "NONE").strip().upper(), r.get("note", "")] for r in csv.DictReader(open(args.csv))}
else:
    c2 = json.load(open(HERE / "out" / "coder2_codes.json"))
PAID = lambda c: c not in ("NONE", "NEUTRALITY_CLAIM")

def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return po, (po - pe) / (1 - pe)

A, B, dis = [], [], []
for r in sheet:
    x, y = c1.get(r["endpoint"], "NONE"), c2[r["id"]][0]
    A.append(x); B.append(y)
    if x != y:
        dis.append({"id": r["id"], "endpoint": r["endpoint"], "coder1": x, "coder2": y, "note2": c2[r["id"]][1]})
po, k = kappa(A, B)
pb, kb = kappa([PAID(x) for x in A], [PAID(y) for y in B])
print(f"servers compared: {len(A)}")
print(f"8-way code : agreement {po:.1%}  Cohen's kappa {k:.2f}")
print(f"paid yes/no: agreement {pb:.1%}  Cohen's kappa {kb:.2f}")
print("coder1 paid:", sum(map(PAID, A)), "| coder2 paid:", sum(map(PAID, B)),
      "| both paid:", sum(PAID(x) and PAID(y) for x, y in zip(A, B)))
with open(HERE / "out" / "disagreements.jsonl", "w") as f:
    for d in dis: f.write(json.dumps(d) + "\n")
print(f"\ndisagreements: {len(dis)}")
for d in dis:
    print(f"  {d['id']} {d['endpoint'][:48]:48} c1={d['coder1']:24} c2={d['coder2']:24} {d['note2'][:60]}")
