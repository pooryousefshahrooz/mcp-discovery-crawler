#!/usr/bin/env python3
"""Minimal, opt-in ad probe: calls ONE free, read-only search tool per server
(fixed allowlist below) to see the sponsored / affiliate content that the
server's metadata says its results contain.

Safety rules (enforced in code):
- only the exact (host, tool) pairs in PLAN may be called; anything else is refused
- never billing, checkout, signup, registration or paid (x402) tools
- one call per server (umesh-malik: search, then fetch the first post)
- raw responses saved per server as soon as each finishes (resumable)
"""
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / dt.date.today().isoformat()
UA = "mcp-discovery-measurement/1.0 (academic research; ad measurement, read-only search tools only)"
PROTO = "2025-06-18"

ROUND1 = [
    ("https://vetclinic.info/mcp", "search_clinics", {"city": "houston", "specialty": "cardiology", "limit": 5}),
    ("https://qubitsok.com/mcp", "searchJobs", {"query": "quantum software engineer", "limit": 5}),
    ("https://pifini.net/api/mcp", "search_places", {"query": "restaurant", "limit": 5}),
    ("https://mcp.nexbid.dev/mcp", "nexbid_search", {"query": "pasta", "max_results": 5}),
    ("https://woebike.de/api/mcp", "search_offers", {"query": "e-bike", "limit": 3}),
    ("https://cashbackpro.org/api/mcp", "search_products", {"query": "phone case", "limit": 3}),
    ("https://mcp.bikefuchs.com/mcp", "search_product", {"q": "bike chain", "country": "DE", "max_results": 3}),
    ("https://picoads.xyz/mcp", "get_recommendations", {"topic": "project management software", "max_results": 3}),
    ("https://utility-matrix.com/mcp", "error-budget-calculator", {"slo_pct": 99.9, "window_days": 30}),
    ("https://mcp.uneed.best/mcp", "search_products", {"query": "note taking", "limit": 5}),
    ("https://www.revuo.ai/api/mcp", "products.search", {"query": "crm"}),
    ("https://focxle.com/api/v1/mcp", "hiring_search_agents", {"query": "web scraping"}),
    ("https://mcp.nomadstays.com/mcp", "getMarketplaceAdverts", {"limit": 5}),
    ("https://www.gigstamp.co.uk/api/mcp", "search_gigs_and_events", {"city": "oxford", "limit": 5}),
    ("https://umesh-malik.com/mcp", "search_posts", {"query": "RAG", "limit": 1}),
]

# Round 2: more ads, only from the servers that returned paid ads in round 1.
NEXBID = "https://mcp.nexbid.dev/mcp"
QUBIT = "https://qubitsok.com/mcp"
ROUND2 = (
    [(NEXBID, "nexbid_search", {"query": q, "max_results": 8}) for q in
     ["pasta", "risotto", "chocolate", "coffee machine", "kitchen knife", "pizza", "salad", "cake",
      "wine", "cheese fondue", "raclette", "blender", "frying pan", "vegan", "bread", "soup",
      "cookbook", "kitchen scale", "espresso", "tea"]]
    + [(QUBIT, "searchJobs", {"query": q, "limit": 8}) for q in
       ["quantum software engineer", "quantum error correction", "photonics engineer",
        "quantum machine learning", "cryogenics engineer", "FPGA engineer",
        "quantum algorithms researcher", "product manager", "superconducting qubits",
        "trapped ion physicist", "quantum sensing", "compiler engineer", "remote", "internship",
        "postdoc"]]
    + [("https://mcp.nomadstays.com/mcp", "getMarketplaceAdverts", {"limit": 50})]
    + [("https://picoads.xyz/mcp", "get_recommendations", {"topic": h, "max_results": 5}) for h in
       ["saas-deals", "productivity-tools", "travel-deals", "agent-tools", "finance-banking", "jobs"]]
    + [("https://umesh-malik.com/mcp", "search_posts", {"query": q, "limit": 1}) for q in
       ["claude code", "mcp", "llm evaluation", "agents"]]
)
ACTIVE_ROUND = "round2"
PLAN = ROUND2 if ACTIVE_ROUND == "round2" else ROUND1
FOLLOWUP = {("https://umesh-malik.com/mcp", "search_posts"): "get_post"}   # fetch first result's slug
ALLOWED = ({(ep, t) for ep, t, _ in ROUND1 + ROUND2}
           | {(ep, t) for (ep, _), t in FOLLOWUP.items()})


def parse(resp):
    text = resp.text
    if "text/event-stream" in resp.headers.get("content-type", ""):
        for line in text.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip()), text
                except json.JSONDecodeError:
                    pass
        return None, text
    try:
        return json.loads(text), text
    except json.JSONDecodeError:
        return None, text


def rpc(client, ep, headers, msg):
    r = client.post(ep, json=msg, headers=headers, timeout=45)
    body, raw = parse(r)
    return {"request": msg, "http_status": r.status_code, "headers": dict(r.headers),
            "response": body, "raw_body": raw[:500000]}, r


def call_tool(client, ep, tool, args):
    if (ep, tool) not in ALLOWED:
        raise RuntimeError(f"refusing non-allowlisted call {ep} {tool}")
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "User-Agent": UA}
    ex = []
    rec, r = rpc(client, ep, h, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                 "params": {"protocolVersion": PROTO, "capabilities": {},
                                            "clientInfo": {"name": "mcp-discovery-measurement", "version": "1.0"}}})
    ex.append(rec)
    if r.headers.get("mcp-session-id"):
        h["Mcp-Session-Id"] = r.headers["mcp-session-id"]
    pv = ((rec["response"] or {}).get("result") or {}).get("protocolVersion")
    if pv:
        h["MCP-Protocol-Version"] = pv
    client.post(ep, json={"jsonrpc": "2.0", "method": "notifications/initialized"}, headers=h, timeout=20)
    rec, _ = rpc(client, ep, h, {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                                 "params": {"name": tool, "arguments": args}})
    ex.append(rec)
    return ex


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with httpx.Client(follow_redirects=True) as client:
        for i, (ep, tool, args) in enumerate(PLAN):
            host = ep.split("/")[2]
            path = OUT / (f"{host}.json" if ACTIVE_ROUND == "round1" else f"round2/{i:02d}_{host}.json")
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                print("skip (done):", ep)
                continue
            res = {"endpoint": ep, "tool": tool, "arguments": args,
                   "called_at": dt.datetime.now(dt.timezone.utc).isoformat()}
            try:
                res["exchanges"] = call_tool(client, ep, tool, args)
                if (ep, tool) in FOLLOWUP:
                    txt = json.dumps(res["exchanges"][-1]["response"])
                    m = re.search(r'slug\\?"\s*:\s*\\?"([^"\\]+)', txt)
                    if m:
                        res["exchanges"] += call_tool(client, ep, FOLLOWUP[(ep, tool)], {"slug": m.group(1)})
            except Exception as e:
                res["error"] = f"{type(e).__name__}: {e}"
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(res, ensure_ascii=False, indent=1))
            os.replace(tmp, path)
            last = (res.get("exchanges") or [{}])[-1]
            print(f"{ep:45} {tool:26} HTTP {last.get('http_status')} {res.get('error', '')}", flush=True)
            time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())
