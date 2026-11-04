#!/usr/bin/env python3
"""S3 - Build the label-free review sheet for the hand coding (two independent coders).

For every signature that needs review (S2) it shows: host, tool, signals, the
link host and path segment, counts, three example contexts from DIFFERENT
responses (and different runs where possible), the tool description and server
instructions from the 2026-09-30 discovery crawl, and the repo/listing URL.
Attribution-only signatures (attrib_utm / src_param only) are listed per host
as a class with one example each, so coders can flag any that are actually ads.

The sheet contains NO status/origin labels. Coders write their codes to
  out/coding_A.json (first coder)  and  out/coding_B.json (second, blind coder)
keyed by signature id. Schema: see CODEBOOK.md.

  python3 analysis/ad_provenance/s3_build_review_sheet.py  -> out/review_sheet.md
  # signatures added after a detector revision, excluding ids already on an earlier sheet:
  python3 analysis/ad_provenance/s3_build_review_sheet.py --exclude out/signatures_v1sheet.csv \
          --out review_sheet_supplement.md
"""
import argparse
import csv
import glob
import json
import random
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "out"
CRAWL = ROOT / "data" / "2026-09-30"


def crawl_meta(host):
    tools, instr = {}, ""
    for f in sorted(glob.glob(str(CRAWL / f"{host}__*.json"))):
        try:
            d = json.load(open(f))
        except (ValueError, OSError):
            continue
        for e in d.get("exchanges", []):
            res = (e.get("response") or {}).get("result") or {}
            if e.get("method") == "initialize":
                instr = instr or res.get("instructions", "") or ""
            for t in res.get("tools", []) or []:
                tools.setdefault(t.get("name"), t.get("description", "") or "")
    return tools, instr


def live_repo():
    m = {}
    for r in csv.DictReader(open(ROOT / "inputs" / "mcp_servers_online_live_2026-09-30.csv")):
        m.setdefault(r["host"], (r.get("repo") or "", r.get("glama_page") or ""))
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude", help="signatures csv whose review ids are already on an earlier sheet")
    ap.add_argument("--out", default="review_sheet.md")
    a = ap.parse_args()
    random.seed(7)
    sigs = list(csv.DictReader(open(OUT / "signatures.csv")))
    done = set()
    if a.exclude:
        done = {s["sig"] for s in csv.DictReader(open(a.exclude)) if s["needs_review"] == "True"}
        done |= {s["sig"] for s in csv.DictReader(open(a.exclude)) if s["needs_review"] != "True"}
    review = {s["sig"]: s for s in sigs if s["needs_review"] == "True" and s["sig"] not in done}
    attrib = [s for s in sigs if s["needs_review"] != "True" and s["sig"] not in done]
    ex = defaultdict(list)
    for line in open(OUT / "candidates.jsonl"):
        c = json.loads(line)
        if c["sig"] in review:
            ex[c["sig"]].append(c)
    repos = live_repo()
    meta_cache = {}
    lines = ["# Ad-provenance review sheet (label-free)", "",
             "Code every `SIG` block per CODEBOOK.md. Examples are raw response excerpts.", ""]
    by_host = defaultdict(list)
    for sk, s in review.items():
        by_host[(s["host"], s["tool"])].append(sk)
    for (host, tool) in sorted(by_host):
        if host not in meta_cache:
            meta_cache[host] = crawl_meta(host)
        tools, instr = meta_cache[host]
        repo, glama = repos.get(host, ("", ""))
        lines += [f"## {host} :: {tool}", "",
                  f"- repo: {repo or '-'}  listing: {glama or '-'}",
                  f"- tool description: {re.sub(r'\\s+', ' ', tools.get(tool, '(not in crawl)'))[:700]}",
                  f"- server instructions: {re.sub(r'\\s+', ' ', instr)[:700] or '-'}", ""]
        for sk in by_host[(host, tool)]:
            s = review[sk]
            items = ex[sk]
            seen, picks = set(), []
            random.shuffle(items)
            for c in sorted(items, key=lambda c: c["run"]):
                if c["rid"] in seen:
                    continue
                seen.add(c["rid"])
                picks.append(c)
            # spread picks over runs
            picks = picks[:: max(1, len(picks) // 3)][:3]
            lines += [f"### SIG {sk}",
                      f"kind={s['kind']} signals={s['signals']} link_host={s['url_host'] or '-'} "
                      f"seg={s['seg']} params={s['param_keys'] or '-'} items={s['n_items']} "
                      f"responses={s['n_responses']}"]
            for c in picks:
                lines += [f"- [{c['run']}] value: `{c['value'][:220]}`",
                          f"  context: {c['context'][:600]}"]
            lines.append("")
    lines += ["## Attribution-only signatures (attrib_utm / src_param), one line each", "",
              "Flag any SIG here that is in fact an ad (else it is coded promotional/attribution by default).", ""]
    for s in attrib:
        lines.append(f"- SIG {s['sig']} {s['host']} :: {s['tool']} [{s['signals']}] link_host={s['url_host']} "
                     f"n={s['n_items']} ex: {s['example'][:260]}")
    (OUT / a.out).write_text("\n".join(lines))
    print(f"review blocks: {len(review)} over {len(by_host)} host-tools; attribution-only: {len(attrib)}")


if __name__ == "__main__":
    main()
