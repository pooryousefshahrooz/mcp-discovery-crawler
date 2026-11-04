#!/usr/bin/env python3
"""RQ3 live probe: does the same server return different ads for different queries?

For every eligible server (rq3_targeting_plan.json) we call its one query tool with
FOUR diverse queries, REPS times each, in INTERLEAVED RANDOMIZED order (to remove any
temporal/ordering bias). All non-query args are held constant. Raw responses are saved
per call, appended+flushed immediately (resumable).

Safety (enforced):
- only the exact (endpoint, tool) in the plan is ever called; query text only varies
- read-only search tools only; never billing/checkout/signup; links are NEVER followed
- follow_redirects=False; GAP seconds between calls; a host is abandoned on first 429
"""
import argparse
import datetime as dt
import json
import random
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
PLAN = HERE / "rq3_targeting_plan.json"
OUTDIR = HERE / "results" / "rq3_targeting"
UA = "mcp-discovery-measurement/1.0 (academic research; ad measurement, read-only search tools only)"
PROTO = "2025-06-18"

# four deliberately different query intents, held identical across every server
QUERIES = {
    "electronics": "wireless bluetooth headphones",
    "travel":      "hotels in paris",
    "clothing":    "women's running shoes",
    "neutral":     "popular picks",
}


def parse(r):
    if "text/event-stream" in r.headers.get("content-type", ""):
        for line in r.text.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except ValueError:
                    pass
        return None
    try:
        return json.loads(r.text)
    except ValueError:
        return None


class Session:
    def __init__(self, client, ep):
        self.c, self.ep, self.id = client, ep, 0
        self.h = {"Content-Type": "application/json",
                  "Accept": "application/json, text/event-stream", "User-Agent": UA}

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


def result_text(body):
    res = (body or {}).get("result") or {}
    txt = "".join(c.get("text", "") for c in res.get("content") or [] if isinstance(c, dict))
    return txt or json.dumps(res, ensure_ascii=False)


def done_keys(path):
    seen = set()
    if path.exists():
        for line in open(path):
            try:
                r = json.loads(line)
                seen.add((r["category"], r["rep"]))
            except (ValueError, KeyError):
                pass
    return seen


def run_server(client, entry, reps, gap, queries, outdir):
    host = entry["host"]
    path = outdir / f"{host}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    already = done_keys(path)
    todo = [(cat, rep) for cat in queries for rep in range(reps) if (cat, rep) not in already]
    if not todo:
        print(f"  [{host}] already complete")
        return
    random.shuffle(todo)  # interleave + randomize query order

    s = Session(client, entry["endpoint"])
    try:
        code = s.open()
    except Exception as e:
        print(f"  [{host}] initialize error: {type(e).__name__}: {e}")
        return
    if code != 200:
        print(f"  [{host}] initialize HTTP {code} -> skip")
        return

    fh = open(path, "a")
    n = 0
    for cat, rep in todo:
        args = dict(entry["base_args"])
        args[entry["query_param"]] = queries[cat]
        try:
            r, body = s.rpc("tools/call", {"name": entry["tool"], "arguments": args})
            status = r.status_code
            text = result_text(body) if status == 200 else ""
        except Exception as e:
            status, text, body = -1, "", {"error": f"{type(e).__name__}: {e}"}
        rec = {"host": host, "endpoint": entry["endpoint"], "tool": entry["tool"],
               "query_param": entry["query_param"], "category": cat, "query": queries[cat],
               "rep": rep, "http": status, "args": args,
               "ts": dt.datetime.now(dt.timezone.utc).isoformat(), "text": text[:200000]}
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fh.flush()
        n += 1
        if status == 429:
            print(f"  [{host}] HTTP 429 -> abandoning host (rate limited)")
            break
        time.sleep(gap)
    fh.close()
    print(f"  [{host}] wrote {n} calls (tool={entry['tool']}, qp={entry['query_param']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--gap", type=float, default=2.5)
    ap.add_argument("--only", default=None, help="comma-separated hosts to run (default: all)")
    ap.add_argument("--mode", choices=["fixed", "domain"], default="fixed",
                    help="fixed = same 4 consumer queries for all; domain = per-server in-domain queries")
    a = ap.parse_args()

    plan = json.load(open(PLAN))
    if a.only:
        want = set(a.only.split(","))
        plan = [p for p in plan if p["host"] in want]

    if a.mode == "domain":
        qmap = json.load(open(HERE / "rq3_domain_queries.json"))
        outdir = HERE / "results" / "rq3_domain"
    else:
        qmap = None  # use fixed QUERIES for every host
        outdir = OUTDIR
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"RQ3 live probe ({a.mode}): {len(plan)} servers x 4 queries x {a.reps} reps "
          f"= up to {len(plan)*4*a.reps} calls; gap={a.gap}s; out={outdir}\n")
    with httpx.Client(follow_redirects=False) as client:
        for i, entry in enumerate(plan, 1):
            queries = qmap.get(entry["host"]) if qmap else QUERIES
            if not queries:
                print(f"[{i}/{len(plan)}] {entry['host']} -> no query map, skip")
                continue
            print(f"[{i}/{len(plan)}] {entry['host']}")
            run_server(client, entry, a.reps, a.gap, queries, outdir)
    print("\ndone.")


if __name__ == "__main__":
    main()
