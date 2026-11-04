#!/usr/bin/env python3
"""Run the FULL ad probe: every call listed in ad_probe/plan_full.json, storing
each call's result (no dedup, so 4 repeats of a tool are all kept).

Safety (enforced here, on top of the plan's offline safety filter):
- a call is sent only if (endpoint, tool, arguments) appears in the plan
- one MCP session per server; >= GAP seconds between calls to the SAME server
- a server is abandoned on its first HTTP 429 or after 3 consecutive errors
- links in results are never fetched or clicked
- each call is written to disk immediately (resumable by line count)

Hosts are probed concurrently (default 6 at a time); calls within one host stay
serial and rate-limited. Results: ad_probe/results/full/<label>/<host>.jsonl

Usage: python3 ad_probe/probe_ads_full.py [LABEL] [PLAN_FILE] [CONCURRENCY]
"""
import collections
import datetime as dt
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

import httpx

HERE = Path(__file__).resolve().parent
UA = "mcp-discovery-measurement/1.0 (academic research; ad measurement, read-only search tools only)"
PROTO = "2025-06-18"
GAP = 2.5


def parse(r):
    t = r.text
    if "text/event-stream" in r.headers.get("content-type", ""):
        for line in t.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except ValueError:
                    pass
        return None
    try:
        return json.loads(t)
    except ValueError:
        return None


class Session:
    def __init__(self, client, ep):
        self.c, self.ep, self.id = client, ep, 0
        self.h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "User-Agent": UA}

    def rpc(self, method, params, notify=False):
        msg = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notify:
            self.id += 1
            msg["id"] = self.id
        r = self.c.post(self.ep, json=msg, headers=self.h, timeout=60)
        return r, (None if notify else parse(r))

    def open(self):
        r, body = self.rpc("initialize", {"protocolVersion": PROTO, "capabilities": {},
                                          "clientInfo": {"name": "mcp-discovery-measurement", "version": "1.0"}})
        if r.headers.get("mcp-session-id"):
            self.h["Mcp-Session-Id"] = r.headers["mcp-session-id"]
        pv = ((body or {}).get("result") or {}).get("protocolVersion")
        if pv:
            self.h["MCP-Protocol-Version"] = pv
        self.rpc("notifications/initialized", {}, notify=True)
        return r.status_code


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    plan = json.load(open(HERE / (sys.argv[2] if len(sys.argv) > 2 else "plan_full.json")))
    concurrency = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    allowed = {(p["endpoint"], p["tool"], json.dumps(p["arguments"], sort_keys=True)) for p in plan}
    out_dir = HERE / "results" / "full" / label
    out_dir.mkdir(parents=True, exist_ok=True)

    by_ep = collections.OrderedDict()
    for p in plan:
        by_ep.setdefault(p["endpoint"], []).append(p)

    totals = collections.Counter()
    tlock = threading.Lock()

    def run_host(item):
        ep, calls = item
        path = out_dir / (urlparse(ep).hostname + ".jsonl")
        done_n = sum(1 for _ in open(path)) if path.exists() else 0   # resume by count
        todo = calls[done_n:]
        if not todo:
            return
        with httpx.Client(follow_redirects=True) as client:
            s = Session(client, ep)
            try:
                if s.open() != 200:
                    with tlock:
                        totals["init_failed"] += 1
                    return
            except httpx.HTTPError:
                with tlock:
                    totals["init_failed"] += 1
                return
            errs = 0
            for c in todo:
                key = (ep, c["tool"], json.dumps(c["arguments"], sort_keys=True))
                if key not in allowed:
                    raise RuntimeError(f"refusing non-planned call {key}")
                time.sleep(GAP)
                try:
                    r, body = s.rpc("tools/call", {"name": c["tool"], "arguments": c["arguments"]})
                    status = r.status_code
                except httpx.HTTPError as e:
                    status, body = None, {"error": str(e)}
                rec = {"endpoint": ep, "tool": c["tool"], "arguments": c["arguments"], "rep": c.get("rep"),
                       "http_status": status, "called_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                       "response": body}
                with open(path, "a") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                with tlock:
                    totals["calls"] += 1
                if status == 429:
                    with tlock:
                        totals["rate_limited_hosts"] += 1
                    break
                errs = errs + 1 if (status != 200 or (body or {}).get("error")) else 0
                if errs >= 3:
                    with tlock:
                        totals["abandoned_3err"] += 1
                    break
        with tlock:
            totals["hosts_done"] += 1
        print(f"  done {ep[:55]:55} (+{len(todo)} calls)", flush=True)

    print(f"hosts: {len(by_ep)} | planned calls: {len(plan)} | concurrency: {concurrency}", flush=True)
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        list(ex.map(run_host, by_ep.items()))
    print("TOTALS:", dict(totals), "->", out_dir, flush=True)


if __name__ == "__main__":
    main()
