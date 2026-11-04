#!/usr/bin/env python3
"""M1 - Load the live ad-metadata probe and decide which responses contain a confirmed ad.

Input : ad_probe/results/meta_2026-11/calls/<host>.jsonl (from ad_probe/meta_probe.py)
Ad detection reuses the provenance study unchanged:
  - S1's text extraction (content[].text, or structuredContent when there is no text)
  - S2's item detector and signature hashing (s2_detect_candidates.detect_items)
  - the adjudicated per-signature codes (ad_provenance/out/final_codes.json)
A response is AD-CONTAINING iff it has >=1 item whose signature is coded confirmed_ad.
Signatures never seen in the provenance study are coded once, by hand, under the same
codebook in coding/new_signature_codes.json; any still uncoded are listed in
out/uncoded_signatures.csv and the script refuses to finish until they are coded.

Each response is also split into its COMPONENTS so M2 can tell where metadata sits:
  text_json   a content[] text block that parses as JSON
  text_plain  a content[] text block that is not JSON (markdown / prose)
  structured  result.structuredContent
  meta        result._meta and content[]._meta (MCP protocol metadata)
  headers     HTTP response headers (transport metadata)

Output: out/responses.jsonl (one line per call), out/uncoded_signatures.csv

  python3 analysis/ad_metadata/m1_detect.py
"""
import csv
import glob
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "ad_provenance"))
from s1_load_responses import parse_rpc        # noqa: E402
from s2_detect_candidates import NEG_LABEL, detect_items  # noqa: E402

CALLS = ROOT / "ad_probe" / "results" / "meta_2026-11" / "calls"
OUT = HERE / "out"
FINAL = HERE.parent / "ad_provenance" / "out" / "final_codes.json"
NEW = HERE / "coding" / "new_signature_codes.json"


def components(rec):
    res = (rec.get("response") or {}).get("result") or {}
    comps = []
    for i, c in enumerate(res.get("content") or []):
        if not isinstance(c, dict):
            continue
        if c.get("type") == "text" and c.get("text"):
            try:
                comps.append({"loc": f"content[{i}]", "kind": "text_json", "data": json.loads(c["text"])})
            except ValueError:
                comps.append({"loc": f"content[{i}]", "kind": "text_plain", "data": c["text"]})
        elif c.get("type") == "resource":
            comps.append({"loc": f"content[{i}].resource", "kind": "text_plain", "data": json.dumps(c["resource"])})
        if c.get("_meta"):
            comps.append({"loc": f"content[{i}]._meta", "kind": "meta", "data": c["_meta"]})
    if res.get("structuredContent") is not None:
        comps.append({"loc": "structuredContent", "kind": "structured", "data": res["structuredContent"]})
    if res.get("_meta"):
        comps.append({"loc": "result._meta", "kind": "meta", "data": res["_meta"]})
    comps.append({"loc": "http_headers", "kind": "headers", "data": rec.get("response_headers") or {}})
    return comps


def main():
    OUT.mkdir(exist_ok=True)
    final = json.load(open(FINAL))
    new = json.load(open(NEW)) if NEW.exists() else {}
    codes = {**{k: v["status"] for k, v in final.items()}, **{k: v["status"] for k, v in new.items()}}
    uncoded, stats = {}, Counter()
    with open(OUT / "responses.jsonl", "w") as fo:
        for f in sorted(glob.glob(str(CALLS / "*.jsonl"))):
            for ln, line in enumerate(open(f)):
                rec = json.loads(line)
                ok, is_err, text = parse_rpc(rec.get("response"))
                rid = hashlib.sha1(f"meta|{Path(f).name}|{ln}".encode()).hexdigest()[:16]
                r = {"rid": rid, "run": "meta_2026-11", "host": rec["host"], "tool": rec["tool"], "text": text,
                     "ok": ok and rec.get("http_status") == 200}
                items = detect_items(r)
                sig_status = {}
                for it, key, _s in items:
                    st = codes.get(it["sig"])
                    sig_status[it["sig"]] = st or "uncoded"
                    if st is None:
                        u = uncoded.setdefault(it["sig"], {"key": key, "n": 0, "example": it["context"][100:600]})
                        u["n"] += 1
                confirmed = sorted(s for s, st in sig_status.items() if st == "confirmed_ad")
                # guard: boilerplate label/disclosure text in a response whose ad container is
                # explicitly empty (e.g. picoads {"sponsored": [], "disclosure_requirement": "...
                # 'Sponsored via picoads'"}) is not an ad
                kinds = {it["kind"] for it, _, _ in items if it["sig"] in confirmed}
                empty_guard = bool(confirmed) and kinds <= {"label", "disclosure", "ad_tool"} and \
                    bool(NEG_LABEL.search(text or ""))
                if empty_guard:
                    confirmed = []
                    stats["empty_container_guard"] += 1
                out = {"rid": rid, **{k: rec[k] for k in ("host", "endpoint", "tool", "tool_category", "arguments",
                                                          "query_id", "rep", "called_at", "http_status")},
                       "ok": r["ok"], "is_error": is_err, "text": text,
                       "ad_containing": bool(confirmed), "confirmed_sigs": confirmed,
                       "items": [{k: it[k] for k in ("kind", "value", "signals", "sig")} for it, _, _ in items
                                 if sig_status[it["sig"]] == "confirmed_ad"],
                       "components": components(rec)}
                fo.write(json.dumps(out, ensure_ascii=False) + "\n")
                stats["calls"] += 1
                stats["ok"] += r["ok"]
                stats["ad_containing"] += out["ad_containing"]
    with open(OUT / "uncoded_signatures.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sig", "host", "tool", "kind", "signals", "url_host", "seg", "param_keys", "n_items", "example"])
        for sk, u in sorted(uncoded.items(), key=lambda kv: kv[1]["key"]):
            w.writerow([sk, *u["key"], u["n"], u["example"]])
    print(dict(stats), "| uncoded signatures:", len(uncoded))
    if uncoded and "--allow-uncoded" not in sys.argv:
        raise SystemExit("code the signatures in out/uncoded_signatures.csv into coding/new_signature_codes.json")


if __name__ == "__main__":
    main()
