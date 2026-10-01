#!/usr/bin/env python3
"""Second pass for paid influence that ads_scan.py misses (e.g. the Emora
network): sponsor relationships, routing users to ANOTHER operator's domain,
partner offers, and external domains promoted by several operators.
Skips servers already in ads_labels.json. Output: out/misses.jsonl"""
import collections
import glob
import json
import re
from pathlib import Path
import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from mcp_paths import data_dir  # noqa: E402
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
DATA = data_dir()
LABELED = {e for v in json.load(open(HERE / "ads_labels.json")).values() for e in v}
I = re.I
PAT = {
    "sponsor_relation": re.compile(
        r"\bsponsored by\b|\bsponsor(ship)? (relationship|of|from)\b|\bin (paid )?partnership with\b|"
        r"\bbrought to you by\b|\bpaid partnership\b|\bfunded by (our )?(partners?|sponsors?|advertis)", I),
    "partner_offer": re.compile(
        r"\b(partner|preferred|featured) (brands?|merchants?|offers?|providers?|products?|lenders?|"
        r"installers?|shops?|stores?|retailers?|vendors?|clinics?|agencies)\b", I),
    "route_elsewhere": re.compile(
        r"\b(route|refer|send|direct|redirect|point|forward|recommend|hand off|handoff)\b[^.\n]{0,15}"
        r"\b(the )?(user|users|them|customer|patient|people|visitor|shopper)s?\b[^.\n]{0,60}?"
        r"(https?://[^\s\"'<>)\]]+)", I),
}
SKIP = re.compile(r"github|gitlab|google|apple|microsoft|openai|anthropic|claude|wikipedia|mozilla|"
                  r"w3\.org|modelcontextprotocol|npmjs|pypi|readthedocs|docs\.|stripe|"
                  r"988lifeline|crisistextline|gov\b|\.gov|who\.int|x\.com|twitter|linkedin|youtube", I)


def reg(host):
    p = (host or "").lower().split(".")
    return ".".join(p[-3:]) if len(p) > 2 and p[-2] in ("co", "com", "org", "net") else ".".join(p[-2:])


def texts(d):
    for ex in d.get("exchanges", []):
        r = (ex.get("response") or {}).get("result")
        if not isinstance(r, dict):
            continue
        if ex["method"] == "initialize" and isinstance(r.get("instructions"), str):
            yield "server_instructions", None, r["instructions"]
        if ex["method"] == "tools/list":
            for t in r.get("tools") or []:
                if isinstance(t, dict) and isinstance(t.get("description"), str):
                    yield "tool_description", t.get("name"), t["description"]


def main():
    out = open(HERE / "out" / "misses.jsonl", "w")
    per = collections.defaultdict(set)
    dom_ops = collections.defaultdict(set)      # external domain -> operators linking to it
    for f in sorted(glob.glob(str(DATA / "*.json"))):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d.get("status") != "ok":
            continue
        ep = d["endpoint"]
        own = reg(urlparse(ep).hostname)
        si = json.dumps(d.get("server_info") or {}).lower()
        for layer, where, text in texts(d):
            for u in re.findall(r"https?://[^\s\"'<>)\]]+", text):
                try:
                    h = reg(urlparse(u).hostname)
                except ValueError:
                    continue
                if h and h != own and not SKIP.search(h) and h.split(".")[0] not in si:
                    dom_ops[h].add(own)
            if ep in LABELED:
                continue
            for k, rx in PAT.items():
                for m in rx.finditer(text):
                    if k == "route_elsewhere":
                        try:
                            tgt = reg(urlparse(m.group(4)).hostname)
                        except ValueError:
                            continue
                        if not tgt or tgt == own or SKIP.search(tgt):
                            continue
                    per[k].add(ep)
                    out.write(json.dumps({"kind": k, "endpoint": ep, "layer": layer, "where": where,
                                          "match": m.group(0)[:200],
                                          "ctx": text[max(0, m.start() - 150): m.end() + 150]},
                                         ensure_ascii=False) + "\n")
    print("new candidate servers per kind:", {k: len(v) for k, v in per.items()})
    print("union:", len(set().union(*per.values())) if per else 0)
    print("\nexternal commercial domains linked by >=3 different operators:")
    for h, ops in sorted(dom_ops.items(), key=lambda kv: -len(kv[1])):
        if len(ops) >= 3:
            print(f"  {len(ops):3}  {h:32} e.g. {sorted(ops)[:4]}")


if __name__ == "__main__":
    main()
