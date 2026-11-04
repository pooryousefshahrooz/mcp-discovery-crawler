#!/usr/bin/env python3
"""Ad-metadata study, step 2: execute ad_probe/plan_meta.json against live servers.

Stores, per call, everything needed to locate metadata later: the JSON-RPC request,
HTTP status, all response headers, the raw HTTP body (SSE or JSON, unparsed), the
parsed JSON-RPC envelope (content[], structuredContent, _meta), and timing.

Safety (same rules as probe_ads_full.py):
- only (endpoint, tool, arguments) present in the plan are ever sent
- one MCP session per server; >= GAP s between calls to the same server
- a server is abandoned on its first HTTP 429 or after 3 consecutive errors
  (one session re-open is attempted first, for expired sessions)
- links in results are never fetched or clicked; no event/report/click tools are called
- each call is appended+flushed immediately; resumable by line count

Output: ad_probe/results/meta_2026-11/calls/<host>.jsonl

  python3 -u ad_probe/meta_probe.py [CONCURRENCY] [host1,host2,...]
"""
import collections
import datetime as dt
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

from probe_ads_full import Session

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "meta_2026-11" / "calls"
GAP = 2.5


def main():
    conc = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    plan = json.load(open(HERE / "plan_meta.json"))
    allowed = {(p["endpoint"], p["tool"], json.dumps(p["arguments"], sort_keys=True)) for p in plan}
    OUT.mkdir(parents=True, exist_ok=True)
    by = collections.OrderedDict()
    for p in plan:
        by.setdefault(p["host"], []).append(p)
    totals, lock = collections.Counter(), threading.Lock()

    only = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
    if only:
        by = collections.OrderedDict((h, c) for h, c in by.items() if h in only)

    def run_host(item):
        host, calls = item
        path = OUT / f"{host}.jsonl"
        if path.exists() and any(json.loads(l).get("http_status") == 429 for l in open(path)):
            return                       # stopped on 429 once: never resumed
        done = sum(1 for _ in open(path)) if path.exists() else 0
        todo = calls[done:]
        if not todo:
            return
        with httpx.Client(follow_redirects=True) as client:
            s = Session(client, calls[0]["endpoint"])
            try:
                s.open()
            except httpx.HTTPError as e:
                print(f"  INIT FAIL {host}: {e}", flush=True)
                return
            errs, reopened = 0, False
            for c in todo:
                key = (c["endpoint"], c["tool"], json.dumps(c["arguments"], sort_keys=True))
                if key not in allowed:
                    raise RuntimeError(f"refusing non-planned call {key}")
                time.sleep(GAP)
                req = {"name": c["tool"], "arguments": c["arguments"]}
                t0 = time.time()
                try:
                    r, body = s.rpc("tools/call", req)
                    status, headers, raw = r.status_code, dict(r.headers), r.text
                except httpx.HTTPError as e:
                    status, headers, raw, body = None, {}, "", {"transport_error": str(e)}
                rec = {**{k: c[k] for k in ("host", "endpoint", "tool", "tool_category", "arguments",
                                            "query_id", "rep", "note")},
                       "request": {"jsonrpc": "2.0", "method": "tools/call", "params": req,
                                   "session_id": s.h.get("Mcp-Session-Id")},
                       "called_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                       "latency_s": round(time.time() - t0, 3), "http_status": status,
                       "response_headers": headers, "raw_body": raw, "response": body}
                with open(path, "a") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    f.flush()
                with lock:
                    totals["calls"] += 1
                if status == 429:
                    print(f"  429 -> abandon {host}", flush=True)
                    with lock:
                        totals["rate_limited"] += 1
                    return
                bad = status != 200 or not isinstance(body, dict) or "error" in body or "transport_error" in body
                errs = errs + 1 if bad else 0
                if errs >= 3:
                    if reopened:
                        print(f"  3 errors -> abandon {host}", flush=True)
                        with lock:
                            totals["abandoned"] += 1
                        return
                    reopened, errs = True, 0
                    s = Session(client, c["endpoint"])
                    try:
                        s.open()
                    except httpx.HTTPError:
                        return
        print(f"  done {host} (+{len(todo)})", flush=True)

    print(f"servers {len(by)} | calls {len(plan)} | concurrency {conc}", flush=True)
    with ThreadPoolExecutor(conc) as ex:
        list(ex.map(run_host, by.items()))
    print("TOTALS", dict(totals), flush=True)


if __name__ == "__main__":
    main()
