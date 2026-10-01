#!/usr/bin/env python3
"""Advertising / paid influence aimed at AI agents, from discovery data only.

Collects every text surface per server (instructions, tool name/description,
input- and output-schema descriptions and property NAMES, _meta keys, prompt
texts, resource descriptions) and flags:

  ad          sponsored / promoted / paid placement / ad slots / ad economics
  affiliate   affiliate, referral fee/code/link, commission
  no_paid     explicit claims of NO paid placement / no affiliate bias
  schema_ad   an outputSchema/_meta property NAME that carries ad data
              (e.g. is_sponsored, promoted, billing_token, affiliate_url)

Writes out/ads_candidates.jsonl (one line per server with hits) for manual
role labelling.
"""
import collections
import glob
import json
import re
from pathlib import Path
import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from mcp_paths import data_dir  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = data_dir()
I = re.I

PAT = {
    "ad": re.compile(
        r"\bsponsored (result|listing|product|placement|slot|block|content|recommendation|link)s?\b|"
        r"\bpromoted (result|listing|product|placement|post|item)s?\b|\bpromoted\b(?= listings? rank)|"
        r"\bpaid (placement|listing|featured|promotion|ranking)s?\b|\bfeatured placement\b|"
        r"\b(ad|ads) (slot|unit|network|inventory|placement|block)s?\b|\bagent-ad\b|\bnative ads?\b|"
        r"\bbilling tokens?\b|\b(cpm|cpc|cpa)\b|\brev(enue)?[- ]share\b|\bearn per (recommendation|click|impression|call)\b|"
        r"\bmonetiz(e|es|ing|ation)\b[^.\n]{0,40}\b(mcp|agent|tool|server)s?\b|\bis_sponsored\b|"
        r"\[sponsored\]|\bpaid promotion\b|\badvertisers?\b[^.\n]{0,40}\b(agent|llm|ai|assistant)s?\b", I),
    "affiliate": re.compile(
        r"\baffiliate (link|url|code|id|program|commission|tag)s?\b|\breferral (fee|code|link|commission|bonus|reward)s?\b|"
        r"\bcommission(s)? (on|from|per|when)\b|\bwe (earn|receive|get) (a )?(commission|fee|referral)\b|"
        r"\bkickbacks?\b|\bpays? (us|[A-Z]\w+) a referral\b", I),
    "no_paid": re.compile(
        r"\b(no|never|not influenced by|without|free of|there is no)\b[^.\n]{0,25}\b(paid placement|sponsored|"
        r"affiliate (bias|links?)|pay-to-rank|advertis(ing|ers))\b|\bnever (paid|sponsored)\b|"
        r"\bpaid placement never\b|\bno ads\b", I),
}
SCHEMA_AD = re.compile(r"^(is_?)?(sponsored|promoted|paid_?placement|premium_?placement)$|"
                       r"^(ad|ads|advert\w*|ad_?(request_?id|label|disclosure|slot|unit|block|creative|"
                       r"impression\w*|click\w*|placement|campaign_?id|id))$|"
                       r"^(billing_?tokens?|affiliate\w*|commission\w*|referral_?(code|link|url|fee|id)|"
                       r"sponsor_?(label|disclosure|name|id)?|is_?featured|featured|disclosure\w*)$", I)


def walk_schema(s, path="$"):
    """Yield (kind, path, value): property names and descriptions."""
    if isinstance(s, dict):
        props = s.get("properties")
        if isinstance(props, dict):
            for k, v in props.items():
                yield "prop", f"{path}.{k}", k
                yield from walk_schema(v, f"{path}.{k}")
        for k, v in s.items():
            if k == "description" and isinstance(v, str):
                yield "desc", path, v
            elif k != "properties" and isinstance(v, (dict, list)):
                yield from walk_schema(v, f"{path}.{k}")
    elif isinstance(s, list):
        for i, v in enumerate(s):
            yield from walk_schema(v, f"{path}[{i}]")


def results(d, method):
    for ex in d.get("exchanges", []):
        if ex.get("method") == method:
            r = (ex.get("response") or {}).get("result")
            if isinstance(r, dict):
                yield r


def surfaces(d, prompts_file):
    for r in results(d, "initialize"):
        if isinstance(r.get("instructions"), str):
            yield "instructions", None, r["instructions"]
        for k in (r.get("_meta") or {}):
            yield "init_meta_key", None, k
    for r in results(d, "tools/list"):
        for t in r.get("tools") or []:
            if not isinstance(t, dict):
                continue
            n = t.get("name")
            yield "tool_name", n, str(n)
            if isinstance(t.get("description"), str):
                yield "tool_description", n, t["description"]
            for kind, p, v in walk_schema(t.get("inputSchema") or {}):
                yield ("input_prop" if kind == "prop" else "input_desc"), f"{n}:{p}", v
            for kind, p, v in walk_schema(t.get("outputSchema") or {}):
                yield ("output_prop" if kind == "prop" else "output_desc"), f"{n}:{p}", v
            for k in (t.get("_meta") or {}):
                yield "tool_meta_key", n, k
    for r in results(d, "resources/list"):
        for x in r.get("resources") or []:
            if isinstance(x, dict) and isinstance(x.get("description"), str):
                yield "resource_description", x.get("uri"), x["description"]
    for r in results(d, "prompts/list"):
        for p in r.get("prompts") or []:
            if isinstance(p, dict) and isinstance(p.get("description"), str):
                yield "prompt_description", p.get("name"), p["description"]
    if prompts_file.exists():
        pd = json.load(open(prompts_file))
        for ex in pd.get("exchanges", []):
            r = (ex.get("response") or {}).get("result")
            if isinstance(r, dict):
                for m in r.get("messages") or []:
                    c = m.get("content") or {}
                    cs = c if isinstance(c, list) else [c]   # some servers send a list of content blocks
                    t = " ".join((x.get("text") or (x.get("resource") or {}).get("text") or "")
                                 for x in cs if isinstance(x, dict)) or None
                    if isinstance(t, str):
                        yield "prompt_message", ex["request"]["params"].get("name"), t


def main():
    out = open(HERE / "out" / "ads_candidates.jsonl", "w")
    n_ok = 0
    per_flag = collections.Counter()
    for f in sorted(glob.glob(str(DATA / "*.json"))):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d.get("status") != "ok":
            continue
        n_ok += 1
        hits = collections.defaultdict(list)
        for surface, where, text in surfaces(d, DATA / "prompts" / Path(f).name):
            if surface in ("output_prop", "input_prop", "tool_meta_key", "init_meta_key"):
                leaf = text.split("/")[-1].split(".")[-1]
                if SCHEMA_AD.match(leaf):
                    hits["schema_ad"].append({"surface": surface, "where": where, "name": text})
                continue
            for flag, rx in PAT.items():
                for m in rx.finditer(text):
                    hits[flag].append({"surface": surface, "where": where, "match": m.group(0),
                                       "ctx": text[max(0, m.start() - 200): m.end() + 200]})
        if hits:
            for k in hits:
                per_flag[k] += 1
            tools = [t.get("name") for r in results(d, "tools/list") for t in r.get("tools") or []
                     if isinstance(t, dict)]
            out.write(json.dumps({"endpoint": d["endpoint"],
                                  "server_info": d.get("server_info"),
                                  "n_tools": len(tools), "tools": tools[:60],
                                  "hits": hits}, ensure_ascii=False) + "\n")
    print(f"servers ok: {n_ok}")
    print("servers per flag:", dict(per_flag))


if __name__ == "__main__":
    main()
