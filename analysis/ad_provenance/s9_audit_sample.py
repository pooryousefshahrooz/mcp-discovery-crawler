#!/usr/bin/env python3
"""S9 - Reproducible hand-audit sample of confirmed ads (precision check).

Draws, with a fixed seed, from the FINAL out/ad_items.csv:
  * all non-operator ads (4 Firecrawl ads), and
  * 40 operator ads, at most 2 per server (so large servers do not dominate),
and writes out/audit_sheet.csv with the raw context of each ad and empty verdict columns:
  is_ad (yes/no) - the item really is a paid/affiliate/sponsored item
  origin_ok (yes/no) - the coded origin is consistent with the raw response
The auditor fills the verdicts in coding/audit_verdicts.csv (sample_id, is_ad, origin_ok, note);
--score prints precision with a Wilson 95% interval.

  python3 analysis/ad_provenance/s9_audit_sample.py          # draw sample
  python3 analysis/ad_provenance/s9_audit_sample.py --score  # score verdicts
"""
import csv
import json
import math
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
SEED = 20261104


def draw():
    ads = list(csv.DictReader(open(OUT / "ad_items.csv")))
    rng = random.Random(SEED)
    non_op = [a for a in ads if a["origin"] != "operator"]
    by = {}
    for a in ads:
        if a["origin"] == "operator":
            by.setdefault(a["server"], []).append(a)
    pool = []
    for h in sorted(by):
        pool += rng.sample(by[h], min(2, len(by[h])))
    rng.shuffle(pool)
    sample = non_op + pool[:40]
    want = {a["server"] for a in sample}
    texts = {}
    for line in open(OUT / "responses.jsonl"):
        r = json.loads(line)
        if r["host"] in want and r["text"]:
            texts.setdefault(r["host"], []).append(r["text"])
    with open(OUT / "audit_sheet.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sample_id", "server", "origin", "identity", "context"])
        for i, a in enumerate(sample):
            probe = a["identity"][5:40] if a["identity"].startswith("item:") else a["example"][:60]
            ctx = ""
            for t in texts.get(a["server"], []):
                k = t.lower().find(probe.lower())
                if k >= 0:
                    ctx = re.sub(r"\s+", " ", t[max(0, k - 300):k + 250])
                    break
            w.writerow([i, a["server"], a["origin"], a["identity"][:160], ctx])
    print(f"sample: {len(sample)} ads ({len(non_op)} non-operator, {min(40, len(pool))} operator) "
          f"-> {OUT / 'audit_sheet.csv'}")


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(c - h, 3), round(c + h, 3)


def score():
    v = list(csv.DictReader(open(HERE / "coding" / "audit_verdicts.csv")))
    n = len(v)
    for col in ("is_ad", "origin_ok"):
        k = sum(x[col] == "yes" for x in v)
        print(f"{col}: {k}/{n}  95% CI {wilson(k, n)}")


if __name__ == "__main__":
    score() if "--score" in sys.argv else draw()
