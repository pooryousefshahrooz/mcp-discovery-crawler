#!/usr/bin/env python3
"""Wide ad-discovery plan (offline; contacts nothing).

Goal: find servers that serve ads WITHOUT declaring them in metadata.
For every open server not already in the ad study, pick ONE tool that
  - the server itself annotates readOnlyHint = true (strict: no heuristics),
  - is not destructive, not priced, not account/personal-data related,
  - has a name suggesting search / recommend / products / deals / offers,
  - needs at most one free-text argument,
and issue ONE commercial query. Servers whose text looks commercial get priority.
Writes ad_probe/plan_wide.json for probe_ads_v2.py (reviewed before running).
"""
import glob
import json
import re
from pathlib import Path
import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from mcp_paths import data_dir  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = data_dir()
LABELS = json.load(open(ROOT / "analysis" / "ads_labels_adjudicated.json"))
DONE = {p["endpoint"] for p in json.load(open(HERE / "plan_v2.json"))}

NAME_OK = re.compile(r"search|find|recommend|product|deal|offer|shop|catalog|compare|discover|suggest|browse|"
                     r"hotel|flight|restaurant|job|event|place|listing", re.I)
ACTION = re.compile(r"\b(buy|purchase|checkout|cart|pay|order|book|reserve|sign ?up|register|login|send|submit|"
                    r"create|delete|remove|update|set|add|post|publish|subscribe|billing|claim|withdraw|transfer|"
                    r"swap|mint|apply|upload|charge|refund|cancel|approve|redeem|click)\b", re.I)
PRIVATE = re.compile(r"profile|account|customer|member|inbox|message|conversation|lead|my_|^my|user|contact|"
                     r"employee|patient|order", re.I)
PRICED = re.compile(r"x402|usdc|\bcredits?\b|\$\s?\d|\bpaid\b(?! placement)|per call|price:|\bfee\b", re.I)
QUERY_ARG = re.compile(r"^(q|query|search|search_query|keyword|keywords|term|topic|text|question)$", re.I)
COMMERCE = re.compile(r"shop|product|buy|deal|coupon|price|store|retail|ecommerce|e-commerce|travel|hotel|flight|"
                      r"restaurant|recommend|review|compare|offer|brand|market|job|real estate|insurance|loan|"
                      r"finance|crypto|saas|software|tool|app", re.I)
QUERIES = {"default": "best", "commerce": "best deals"}


def main():
    labelled = {e for v in LABELS.values() for e in v}
    plan = []
    for f in sorted(glob.glob(str(DATA / "*.json"))):
        try:
            d = json.load(open(f))
        except (ValueError, OSError):
            continue
        ep = d["endpoint"]
        if d.get("status") != "ok" or ep in DONE:
            continue
        init = (d["exchanges"][0].get("response") or {}).get("result") or {}
        tools = [t for e in d["exchanges"] if e["method"] == "tools/list"
                 for t in ((e.get("response") or {}).get("result") or {}).get("tools") or [] if isinstance(t, dict)]
        text = (init.get("instructions") or "") + " " + " ".join((t.get("description") or "")[:200] for t in tools)
        commerce = bool(COMMERCE.search(text))
        best = None
        for t in tools:
            name, desc = t.get("name", ""), t.get("description") or ""
            ann = t.get("annotations") or {}
            if ann.get("readOnlyHint") is not True or ann.get("destructiveHint") is True:
                continue
            if not NAME_OK.search(name) or ACTION.search(name.replace("-", "_").replace(".", "_")) \
                    or PRIVATE.search(name) or PRICED.search(desc):
                continue
            sch = t.get("inputSchema") or {}
            props, req = sch.get("properties") or {}, sch.get("required") or []
            qargs = [r for r in req if QUERY_ARG.match(r) and (props.get(r) or {}).get("type", "string") == "string"]
            if len(req) > 1 or (req and not qargs):
                continue
            if not req:
                opt = [k for k in props if QUERY_ARG.match(k) and (props[k] or {}).get("type", "string") == "string"]
                qargs = opt[:1]
            args = {qargs[0]: QUERIES["commerce" if commerce else "default"]} if qargs else {}
            for k in ("limit", "max_results", "count", "per_page", "page_size", "top_k"):
                if k in props and (props[k] or {}).get("type") in ("integer", "number"):
                    args[k] = 5
            best = {"endpoint": ep, "tool": name, "arguments": args, "read_only_hint": True,
                    "commerce": commerce, "labelled_paid": ep in labelled}
            break
        if best:
            plan.append(best)
    plan.sort(key=lambda p: not p["commerce"])
    json.dump(plan, open(HERE / "plan_wide.json", "w"), indent=1, ensure_ascii=False)
    print(f"wide plan: {len(plan)} servers, 1 call each ({sum(p['commerce'] for p in plan)} commerce-looking)")
    for p in plan[:15]:
        print("  ", p["endpoint"][:55], p["tool"], p["arguments"])


if __name__ == "__main__":
    main()
