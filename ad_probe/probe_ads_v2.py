#!/usr/bin/env python3
"""Expanded ad probe: runs ONLY the calls listed in ad_probe/plan_v2.json
(built and reviewed offline by build_plan.py).

Safety rules (enforced here, on top of the plan filter):
- a call is sent only if (endpoint, tool, arguments) is literally in the plan
- one MCP session per server; >= GAP seconds between calls to the same server
- a server is abandoned on its first HTTP 429 or on 3 consecutive errors
- links in results are never fetched or clicked
- each result is written to disk immediately (resumable)

Usage: python3 ad_probe/probe_ads_v2.py [RUN_LABEL] [PLAN_FILE]
       (default label: today's date; default plan: plan_v2.json)
Results: ad_probe/results/v2/<RUN_LABEL>/<host>.jsonl
"""
import collections
import datetime as dt
import json
import sys
import time
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
    plan = json.load(open(HERE / (sys.argv[2] if len(sys.argv) > 2 else "plan_v2.json")))
    allowed = {(p["endpoint"], p["tool"], json.dumps(p["arguments"], sort_keys=True)) for p in plan}
    out_dir = HERE / "results" / "v2" / label
    out_dir.mkdir(parents=True, exist_ok=True)
    by_ep = collections.OrderedDict()
    for p in plan:
        by_ep.setdefault(p["endpoint"], []).append(p)
    with httpx.Client(follow_redirects=True) as client:
        for ep, calls in by_ep.items():
            path = out_dir / (urlparse(ep).hostname + ".jsonl")
            done = set()
            if path.exists():
                done = {json.dumps([x["tool"], x["arguments"]], sort_keys=True) for x in map(json.loads, open(path))}
            todo = [c for c in calls if json.dumps([c["tool"], c["arguments"]], sort_keys=True) not in done]
            if not todo:
                continue
            s, errs, stopped = Session(client, ep), 0, ""
            try:
                st = s.open()
            except httpx.HTTPError as e:
                print(f"{ep}: initialize failed {e}"); continue
            if st != 200:
                print(f"{ep}: initialize HTTP {st}"); continue
            n = 0
            for c in todo:
                key = (ep, c["tool"], json.dumps(c["arguments"], sort_keys=True))
                if key not in allowed:                      # defence in depth
                    raise RuntimeError(f"refusing non-planned call {key}")
                time.sleep(GAP)
                try:
                    r, body = s.rpc("tools/call", {"name": c["tool"], "arguments": c["arguments"]})
                    status = r.status_code
                except httpx.HTTPError as e:
                    status, body = None, {"error": str(e)}
                rec = {"endpoint": ep, "tool": c["tool"], "arguments": c["arguments"], "http_status": status,
                       "called_at": dt.datetime.now(dt.timezone.utc).isoformat(), "response": body}
                with open(path, "a") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
                if status == 429:
                    stopped = "HTTP 429 (rate limited) -> stopping this server"; break
                errs = errs + 1 if status != 200 or (body or {}).get("error") else 0
                if errs >= 3:
                    stopped = "3 consecutive errors -> stopping this server"; break
            print(f"{ep[:55]:55} calls={n} {stopped}", flush=True)


if __name__ == "__main__":
    main()
