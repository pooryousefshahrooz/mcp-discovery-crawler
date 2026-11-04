#!/usr/bin/env python3
"""Ad-metadata study, step 0: live tools/list on every confirmed-ad server.

Eligible servers = the 51 servers with >=1 confirmed ad in the v2 provenance study
(analysis/ad_provenance/out/ad_provenance_results.csv). For each we open one MCP
session and record initialize + tools/list (no tool is called). Used to confirm
reachability and the current input schema of each confirmed ad-serving tool.

Output (append+flush, one line per server): ad_probe/results/meta_2026-11/tools_list.jsonl

  python3 ad_probe/meta_tools_list.py
"""
import csv
import datetime as dt
import glob
import json
from pathlib import Path
from urllib.parse import urlparse

import httpx

from probe_ads_full import Session

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROV = ROOT / "analysis" / "ad_provenance" / "out" / "ad_provenance_results.csv"
OUT_DIR = HERE / "results" / "meta_2026-11"


def endpoints():
    """host -> endpoint, taken from earlier probe records (no guessing)."""
    hosts = {r["server"] for r in csv.DictReader(open(PROV))}
    ep = {}
    for f in sorted(glob.glob(str(HERE / "results" / "**" / "*.jsonl"), recursive=True)):
        for line in open(f):
            try:
                e = json.loads(line).get("endpoint")
            except ValueError:
                continue
            if e and urlparse(e).hostname in hosts:
                ep.setdefault(urlparse(e).hostname, e.rstrip("/") if e.endswith("/mcp/") else e)
    from meta_build_plan import EXTRA
    for h, (e, _c, _o) in EXTRA.items():
        ep.setdefault(h, e)
    return ep


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "tools_list.jsonl"
    done = {json.loads(l)["host"] for l in open(out)} if out.exists() else set()
    for host, ep in sorted(endpoints().items()):
        if host in done:
            continue
        rec = {"host": host, "endpoint": ep, "at": dt.datetime.now(dt.timezone.utc).isoformat()}
        try:
            with httpx.Client(follow_redirects=True) as c:
                s = Session(c, ep)
                rec["init_status"] = s.open()
                r, body = s.rpc("tools/list", {})
                rec["status"], rec["tools"] = r.status_code, ((body or {}).get("result") or {}).get("tools")
        except httpx.HTTPError as e:
            rec["error"] = str(e)
        with open(out, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"{host:42} init={rec.get('init_status')} tools={len(rec.get('tools') or [])}", flush=True)


if __name__ == "__main__":
    main()
