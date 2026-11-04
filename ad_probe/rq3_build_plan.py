#!/usr/bin/env python3
"""Build the RQ3 (query-targeting) live-probe plan.

Universe: every host that returned a commercial/tracking candidate in the
2026-10-29 full run AND exposes a free-text query/search tool whose required
arguments we can safely fill. We collapse the single-operator wo*.de family to
a few representatives so it does not dominate the paired plot.

Output: rq3_targeting_plan.json  (list of {host, endpoint, tool, query_param, base_args, serves_ads_prior})
"""
import glob
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parent / "fresh_measurement" / "runs" / "2026-10-29-full"
EPDIR = RUN / "endpoints"

QUERY_KEYS = ("query", "q", "topic", "search", "term", "keyword", "text", "pattern", "niche")
# required params we know how to fill safely (read-only, generic)
SAFE_DEFAULTS = {
    "limit": 5, "max_results": 5, "maxResults": 5, "count": 5, "top_k": 5, "n": 5,
    "country": "US", "locale": "en", "lang": "en", "language": "en",
    "content_type": "all", "type": "all", "category": "all",
}


def load_candidates():
    d = json.load(open(RUN / "ad_candidates.json"))
    # host -> {tools that produced a candidate, strict?}
    host_tools = defaultdict(set)
    host_strict = defaultdict(bool)
    for r in d:
        h = r["endpoint"].split("/")[2]
        host_tools[h].add(r["tool"])
        if r.get("commercial_candidate") is True:
            host_strict[h] = True
    return host_tools, host_strict


def endpoint_file(host):
    fs = glob.glob(str(EPDIR / f"{host}__*"))
    return fs[0] if fs else None


def pick_query_param(schema):
    props = (schema or {}).get("properties", {}) or {}
    required = set((schema or {}).get("required", []) or [])
    # prefer a required string prop whose name is query-like
    cands = [p for p in props if p.lower() in QUERY_KEYS]
    # order: required query-like first, then any query-like
    cands.sort(key=lambda p: (p not in required, QUERY_KEYS.index(p.lower()) if p.lower() in QUERY_KEYS else 99))
    for p in cands:
        if props[p].get("type", "string") in ("string", None):
            return p
    return None


def fill_required(schema, query_param):
    """Return base_args filling every REQUIRED param except the query param, or None if unfillable."""
    props = (schema or {}).get("properties", {}) or {}
    required = [p for p in (schema or {}).get("required", []) or [] if p != query_param]
    args = {}
    for p in required:
        spec = props.get(p, {})
        if p in SAFE_DEFAULTS:
            args[p] = SAFE_DEFAULTS[p]
        elif "default" in spec:
            args[p] = spec["default"]
        elif spec.get("enum"):
            args[p] = spec["enum"][0]
        elif spec.get("type") == "integer" or spec.get("type") == "number":
            args[p] = 5
        elif spec.get("type") == "boolean":
            args[p] = False
        else:
            return None  # a required param we can't safely fill -> skip server
    # also add a sensible result cap if the tool supports one (non-required) so lists are returned
    for cap in ("limit", "max_results", "maxResults", "count", "top_k"):
        if cap in props and cap not in args:
            args[cap] = 5
            break
    return args


def collapse_wo_family(plan):
    """Keep only 3 representatives of the wo*.de single-operator family."""
    wo = [p for p in plan if re.match(r"^wo[a-z]+\.de$", p["host"])]
    keep = {"woebike.de", "wostrom.de", "wovitamine.de"}
    return [p for p in plan if not re.match(r"^wo[a-z]+\.de$", p["host"]) or p["host"] in keep]


def main():
    host_tools, host_strict = load_candidates()
    plan = []
    skipped = []
    for host in sorted(host_tools):
        f = endpoint_file(host)
        if not f:
            skipped.append((host, "no endpoint file"))
            continue
        d = json.load(open(f))
        tools = {t["name"]: t for t in d.get("tools", [])}
        chosen = None
        # prefer a 'search'-named tool, then 'find', then the rest (alphabetical within tier)
        def _rank(n):
            nl = n.lower()
            return (0 if "search" in nl else 1 if "find" in nl else 2, nl)
        for tname in sorted(host_tools[host], key=_rank):
            t = tools.get(tname)
            if not t:
                continue
            qp = pick_query_param(t.get("inputSchema", {}))
            if not qp:
                continue
            base = fill_required(t.get("inputSchema", {}), qp)
            if base is None:
                continue
            chosen = {"host": host, "endpoint": d["endpoint"], "tool": tname,
                      "query_param": qp, "base_args": base,
                      "serves_ads_prior": bool(host_strict[host])}
            break
        if chosen:
            plan.append(chosen)
        else:
            skipped.append((host, "no fillable query tool"))

    plan = collapse_wo_family(plan)
    out = HERE / "rq3_targeting_plan.json"
    out.write_text(json.dumps(plan, indent=1))
    print(f"eligible servers in plan: {len(plan)}  (strict-ad: {sum(p['serves_ads_prior'] for p in plan)})")
    print(f"skipped: {len(skipped)}")
    for p in plan:
        print(f"  {p['host']:40} {p['tool']:26} qp={p['query_param']:8} base={p['base_args']} ads_prior={p['serves_ads_prior']}")
    print(f"\nplan -> {out}")


if __name__ == "__main__":
    main()
