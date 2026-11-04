#!/usr/bin/env python3
"""S1 - Load EVERY recorded tool-call response into one normalized file.

Sources (all under ad_probe/results/, nothing is re-probed):
  A. per-call JSONL with a JSON-RPC `response`   (full/*, v2/*)
  B. rq3 JSONL with the result text in `text`    (rq3_domain, rq3_fixed, rq3_targeting)
  C. early one-file-per-call JSON with `exchanges` (2026-09-30, 2026-09-30/round2);
     only the tools/call exchange is used, and an SSE `raw_body` is parsed when
     `response` is empty.
Excluded: nexbid_probe.jsonl / qubitsok_probe.jsonl (derived summaries, no raw text).
Frozen snapshot: run directories created after the double coding (EXCLUDE_RUNS) are left out,
so every analysed signature was coded by both coders. Add them only with a new coding round.

Output: out/responses.jsonl, one line per tool call:
  {rid, run, host, tool, arguments, called_at, ok, is_error, text}
  rid = sha1(run|file|line) - a stable id used by every later stage.

  python3 analysis/ad_provenance/s1_load_responses.py
"""
import glob
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RES = ROOT / "ad_probe" / "results"
OUT = HERE / "out"
# added 2026-11-04 by the ad_metadata workstream, after this study's coding round
EXCLUDE_RUNS = ("meta_2026-11",)
# calls recorded after the first review sheet was built (17:16:57 +0100) were never coded;
# rq3_domain kept receiving appends from a concurrent probe after that point
FREEZE_UTC = "2026-11-04T16:16:57"


def text_of_result(res):
    if not isinstance(res, dict):
        return ""
    parts = [c.get("text", "") for c in res.get("content") or [] if isinstance(c, dict)]
    t = "".join(p for p in parts if p)
    if not t and res.get("structuredContent") is not None:
        t = json.dumps(res["structuredContent"], ensure_ascii=False)
    return t


def parse_rpc(resp):
    """-> (ok, is_error, text) from a JSON-RPC response object."""
    if not isinstance(resp, dict):
        return False, False, ""
    if "error" in resp:
        return False, True, json.dumps(resp["error"], ensure_ascii=False)
    res = resp.get("result") or {}
    return True, bool(res.get("isError")), text_of_result(res)


def parse_sse(raw):
    for line in (raw or "").splitlines():
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except ValueError:
                continue
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def rid(*parts):
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:16]


def main():
    OUT.mkdir(exist_ok=True)
    stats = Counter()
    with open(OUT / "responses.jsonl", "w") as fo:
        def emit(rec):
            fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
            stats[rec["run"]] += 1

        # A + B: JSONL files
        for f in sorted(glob.glob(str(RES / "**" / "*.jsonl"), recursive=True)):
            p = Path(f)
            if p.parent == RES:          # top-level derived summaries
                continue
            run = str(p.parent.relative_to(RES))
            if run.startswith(EXCLUDE_RUNS):
                stats["_excluded_after_coding"] += 1
                continue
            host = p.name[:-6]
            for i, line in enumerate(open(f)):
                try:
                    r = json.loads(line)
                except ValueError:
                    stats["_bad_json"] += 1
                    continue
                if "response" in r:
                    ok, err, t = parse_rpc(r.get("response"))
                    args = r.get("arguments", {})
                elif "text" in r:
                    t = r.get("text") or ""
                    ok, err = bool(t) and r.get("http") in (200, None), False
                    t = t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)
                    args = r.get("args", {})
                else:
                    stats["_unknown_format"] += 1
                    continue
                when = (r.get("called_at") or r.get("ts") or "")[:19]
                if when and when > FREEZE_UTC:
                    stats["_after_freeze"] += 1
                    continue
                emit({"rid": rid(run, p.name, i), "run": run, "host": host, "tool": r.get("tool"),
                      "arguments": args, "called_at": r.get("called_at") or r.get("ts"),
                      "ok": ok, "is_error": err, "text": t})

        # C: early per-file JSON
        for f in sorted(glob.glob(str(RES / "2026-09-30" / "**" / "*.json"), recursive=True)):
            p = Path(f)
            run = str(p.parent.relative_to(RES))
            try:
                d = json.load(open(f))
            except ValueError:
                stats["_bad_json"] += 1
                continue
            host = p.stem.split("_", 1)[1] if p.stem[:2].isdigit() and "_" in p.stem else p.stem
            # a file can hold several tools/call exchanges (e.g. search_posts then get_post):
            # take the tool name and arguments from each request, not from the file header
            for j, e in enumerate(d.get("exchanges", [])):
                req = e.get("request") or {}
                if req.get("method") != "tools/call":
                    continue
                params = req.get("params") or {}
                resp = e.get("response") or parse_sse(e.get("raw_body"))
                ok, err, t = parse_rpc(resp)
                emit({"rid": rid(run, p.name, j), "run": run, "host": host,
                      "tool": params.get("name") or d.get("tool"),
                      "arguments": params.get("arguments", d.get("arguments", {})),
                      "called_at": d.get("called_at"), "ok": ok, "is_error": err, "text": t})
    json.dump(dict(stats), open(OUT / "s1_stats.json", "w"), indent=1)
    print(f"tool calls loaded: {sum(v for k, v in stats.items() if not k.startswith('_'))}")
    print({k: v for k, v in stats.items() if k.startswith("_")})


if __name__ == "__main__":
    main()
