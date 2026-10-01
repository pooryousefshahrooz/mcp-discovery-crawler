#!/usr/bin/env python3
"""Blind coding sheet for the paid-content labelling (see ads_codebook.md).

Every server flagged by ads_scan.py / ads_misses.py (plus every server already in
ads_labels.json) gets one row with label-free evidence lines, in shuffled order.

Usage:
  python3 analysis/build_coding_sheet.py
      -> analysis/coding_sheet.csv (+ out/coding_sheet.jsonl), ids S000...
  # after a new crawl: only servers that are not in earlier sheets
  python3 analysis/build_coding_sheet.py --name coding_sheet_new --prefix N \
      --exclude out/coding_sheet.jsonl
A human coder fills the `code` and `note` columns of the CSV.
"""
import argparse
import csv
import glob
import json
import random
import re
from pathlib import Path
import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from mcp_paths import data_dir  # noqa: E402

HERE = Path(__file__).resolve().parent
EVID = re.compile(r"sponsor|promot|paid (placement|listing)|featured|advertis|\bads?\b|affiliate|referral|"
                  r"commission|kickback|rev(enue)?[- ]share|earn|monetiz|partner|competitor|route the user|"
                  r"direct (the )?users? to|disclos|billing token|cpm|cpc|cpa\b|no paid|never paid", re.I)
SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def evidence(d, prompts_file):
    ev = []
    for ex in d["exchanges"]:
        r = (ex.get("response") or {}).get("result")
        if not isinstance(r, dict):
            continue
        if ex["method"] == "initialize" and r.get("instructions"):
            ev += ["[instructions] " + s.strip()[:300] for s in SPLIT.split(r["instructions"]) if EVID.search(s)]
        if ex["method"] == "tools/list":
            for t in r.get("tools") or []:
                if not isinstance(t, dict):
                    continue
                ev += [f"[tool {t.get('name')}] " + s.strip()[:300]
                       for s in SPLIT.split(t.get("description") or "") if EVID.search(s)]
                fields = sorted(set(re.findall(
                    r'"((?:is_)?(?:sponsored|promoted|affiliate\w*|referral\w*|commission\w*|'
                    r'billing_token|disclosure\w*|featured|is_featured|ad_id|adRequestId|sponsor))"',
                    json.dumps(t.get("outputSchema") or {}))))
                if fields:
                    ev.append(f"[output fields of {t.get('name')}] " + ", ".join(fields))
                for m in re.finditer(r'"(\w*(?:referr|affiliat|commission|sponsor|promo)\w*)":\s*\{[^{}]*?'
                                     r'"description":\s*"([^"]{0,200})', json.dumps(t.get("inputSchema") or {}), re.I):
                    ev.append(f"[input field {t.get('name')}.{m.group(1)}] {m.group(2)}")
    if prompts_file.exists():
        for ex in json.load(open(prompts_file)).get("exchanges", []):
            r = (ex.get("response") or {}).get("result") or {}
            for m in r.get("messages") or []:
                c = m.get("content") or {}
                t = " ".join(x.get("text", "") for x in (c if isinstance(c, list) else [c]) if isinstance(x, dict))
                ev += [f"[prompt {ex['request']['params'].get('name')}] " + s.strip()[:300]
                       for s in SPLIT.split(t) if EVID.search(s)]
    seen, out = set(), []
    for e in ev:
        k = e.split("] ", 1)[1][:120]
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out[:10]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="coding_sheet", help="output base name")
    ap.add_argument("--prefix", default="S", help="row id prefix")
    ap.add_argument("--exclude", nargs="*", default=[], help="earlier out/*.jsonl sheets whose servers to skip")
    a = ap.parse_args()
    data = data_dir()
    eps = {json.loads(l)["endpoint"] for l in open(HERE / "out" / "ads_candidates.jsonl")}
    eps |= {json.loads(l)["endpoint"] for l in open(HERE / "out" / "misses.jsonl")}
    eps |= {e for v in json.load(open(HERE / "ads_labels.json")).values() for e in v}
    for sheet in a.exclude:
        eps -= {json.loads(l)["endpoint"] for l in open(HERE / sheet)}
    rows = []
    for f in glob.glob(str(data / "*.json")):
        try:
            d = json.load(open(f))
        except (ValueError, OSError):
            continue
        if d["endpoint"] not in eps:
            continue
        rows.append({"endpoint": d["endpoint"], "server_name": (d.get("server_info") or {}).get("name"),
                     "n_tools": sum(len(((ex.get("response") or {}).get("result") or {}).get("tools") or [])
                                    for ex in d["exchanges"] if ex["method"] == "tools/list"),
                     "evidence": evidence(d, data / "prompts" / Path(f).name)})
    random.seed(20260930)
    random.shuffle(rows)
    for i, r in enumerate(rows):
        r["id"] = f"{a.prefix}{i:03d}"
    with open(HERE / "out" / f"{a.name}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(HERE / f"{a.name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "endpoint", "server_name", "n_tools", "evidence", "code", "note"])
        for r in rows:
            w.writerow([r["id"], r["endpoint"], r["server_name"], r["n_tools"], "\n".join(r["evidence"]), "", ""])
    print(len(rows), "servers in", f"{a.name}.csv;", sum(1 for r in rows if not r["evidence"]), "with no evidence lines")


if __name__ == "__main__":
    main()
