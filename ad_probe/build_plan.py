#!/usr/bin/env python3
"""Build an expanded, safe ad-probe plan (offline; contacts nothing).

For every working server labelled as carrying paid content
(analysis/ads_labels_adjudicated.json), select tools that look like free,
read-only search / list / recommend tools, and generate up to Q queries each.

Safety filter (a tool is dropped if ANY applies):
  - annotations.destructiveHint is true, or readOnlyHint is explicitly false
  - name or description suggests an action: buy/checkout/pay/order/book/sign up/
    register/send/submit/create/delete/update/billing/claim/withdraw/transfer/...
  - description mentions a price or payment rail (x402, USDC, credits, $, "paid")
  - it has a required argument we cannot fill with a plain search term or an enum
Writes ad_probe/plan_v2.json and prints a summary for review before running.
"""
import collections
import glob
import json
import re
from pathlib import Path
import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from mcp_paths import data_dir  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = data_dir()
LABELS = json.load(open(ROOT / "analysis" / "ads_labels_adjudicated.json"))
Q = 10

NAME_OK = re.compile(r"search|find|list|get|lookup|recommend|browse|query|discover|explore|offers?|deals?|"
                     r"adverts?|catalog|products?|jobs?|places?|events?|gigs?|tariffs?|promotions?|trending", re.I)
ACTION = re.compile(r"\b(buy|purchase|checkout|cart|pay|payment|order|book|booking|reserve|sign ?up|signup|register|"
                    r"login|send|submit|create|delete|remove|update|set|add|post|publish|subscribe|billing|bill|fire|"
                    r"claim|withdraw|transfer|swap|mint|apply|invite|upload|charge|refund|cancel|approve|redeem|"
                    r"track_click|click)\b|_(create|delete|update|send|buy|order|book|pay|register)", re.I)
PRIVATE = re.compile(r"profile|workspace|subscription|negotiation|account|\bmy_|^my|jobs\.list|subcontractor|"
                     r"customer|member|inbox|message|conversation|lead|inquir|reminder", re.I)   # may expose account/personal data
EXCLUDE_SERVERS = {"https://mcp.checklyra.com/mcp", "https://adminsubstitute.com/api/v1/mcp"}   # returns real people's gift profiles
PRICED = re.compile(r"x402|usdc|\bcredits?\b|\$\s?\d|\bpaid\b(?! placement)|per call|costs? \d|price:|\bfee\b", re.I)
QUERY_ARG = re.compile(r"^(q|query|search|search_query|keyword|keywords|term|topic|text|prompt|question|"
                       r"product|category|city|destination|location)$", re.I)
GENERIC = ["best", "cheap", "popular", "new", "top rated", "recommended", "beginner", "professional", "gift", "deal"]
DOMAIN_QUERIES = {   # meaningful queries for the two servers with auction / promoted ads
    "https://mcp.nexbid.dev/mcp": ["pasta", "coffee", "chocolate", "knife", "pizza", "wine", "cheese", "bread",
                                   "tea", "vegan"],
    "https://qubitsok.com/mcp": ["quantum software engineer", "error correction", "photonics", "cryogenics",
                                 "FPGA", "quantum algorithms", "product manager", "superconducting",
                                 "trapped ion", "quantum sensing"],
}
STOP = set(("the a an and or for with to of in on your you our mcp server tool tools api data from by is are this "
            "that it as at be can use using get find search list all any more best new free when returns return "
            "requires required human published each only which what will have into also other these their them "
            "then than there here after before used such like call calls result results user users does default "
            "optional true false null string number field fields value values including include includes where "
            "every must should never always first next page pages limit query id ids slug url urls name names "
            "details detail full match matching given based within about over under").split())


def words_for(server_text):
    ws = [w for w in re.findall(r"[a-z][a-z-]{3,}", server_text.lower()) if w not in STOP]
    return [w for w, _ in collections.Counter(ws).most_common(12)]


def main():
    paid = {e for k, v in LABELS.items() if k != "neutrality_claim" for e in v}
    plan, dropped = [], collections.Counter()
    for f in glob.glob(str(DATA / "*.json")):
        d = json.load(open(f))
        ep = d["endpoint"]
        if ep not in paid or ep in EXCLUDE_SERVERS or d.get("status") != "ok":
            continue
        init = (d["exchanges"][0].get("response") or {}).get("result") or {}
        tools = [t for e in d["exchanges"] if e["method"] == "tools/list"
                 for t in ((e.get("response") or {}).get("result") or {}).get("tools") or [] if isinstance(t, dict)]
        text = (init.get("instructions") or "") + " " + " ".join((t.get("description") or "")[:300] for t in tools)
        topical = words_for(text)
        picked = 0
        for t in tools:
            name, desc = t.get("name", ""), t.get("description") or ""
            ann = t.get("annotations") or {}
            if ann.get("destructiveHint") is True or ann.get("readOnlyHint") is False:
                dropped["destructive/not-readonly"] += 1; continue
            if not NAME_OK.search(name) or ACTION.search(name.replace("-", "_")) or ACTION.search(desc[:200]):
                dropped["not a search tool / action"] += 1; continue
            if PRIVATE.search(name):
                dropped["may expose account/personal data"] += 1; continue
            if PRICED.search(desc):
                dropped["priced"] += 1; continue
            sch = t.get("inputSchema") or {}
            props, req = sch.get("properties") or {}, sch.get("required") or []
            qarg, fixed, ok = None, {}, True
            for r in req:
                p = props.get(r) or {}
                if QUERY_ARG.match(r) and p.get("type", "string") == "string" and not p.get("enum"):
                    qarg = qarg or r
                elif isinstance(p.get("enum"), list) and p["enum"]:
                    fixed[r] = p["enum"][0]
                else:
                    ok = False
            if not ok:
                dropped["unfillable required arg"] += 1; continue
            if not qarg:
                opt = [k for k in props if QUERY_ARG.match(k) and (props[k] or {}).get("type", "string") == "string"
                       and not (props[k] or {}).get("enum")]
                qarg = opt[0] if opt else None
            for k in ("limit", "max_results", "count", "per_page", "page_size", "top_k"):
                if k in props and (props[k] or {}).get("type") in ("integer", "number"):
                    fixed[k] = 5
            queries = (DOMAIN_QUERIES.get(ep, GENERIC))[:Q] if qarg else [None]
            for q in queries:
                args = dict(fixed)
                if qarg:
                    args[qarg] = q
                plan.append({"endpoint": ep, "tool": name, "arguments": args,
                             "read_only_hint": ann.get("readOnlyHint")})
            picked += 1
            if picked >= 2:          # at most 2 tools per server
                break
    json.dump(plan, open(HERE / "plan_v2.json", "w"), indent=1, ensure_ascii=False)
    by = collections.Counter(p["endpoint"] for p in plan)
    print(f"servers in plan: {len(by)} / {len(paid)} paid-labelled | calls: {len(plan)}")
    print("dropped tools:", dict(dropped))
    for ep, n in by.most_common():
        tools = sorted({p['tool'] for p in plan if p['endpoint'] == ep})
        ex = next(p["arguments"] for p in plan if p["endpoint"] == ep)
        print(f"  {n:3}  {ep[:52]:52} {tools}  e.g. {json.dumps(ex)[:70]}")


if __name__ == "__main__":
    main()
