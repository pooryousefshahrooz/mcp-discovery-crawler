#!/usr/bin/env python3
"""Further advertising angles in discovery data (candidates for manual review).

  reply_branding   instructions that put brand text / CTA / links into the
                   model's reply ("end your response with", "Powered by", ...)
  upsell           upgrade / cross-sell / sister-service directives
  agent_seo        superlative or comparative marketing aimed at tool choice
  tracking_url     URLs in metadata carrying attribution params (utm_*, ref, src ...)
  lead_gen         tools that collect contact PII for partners / referral fees
  clone_cluster    near-identical listings across different hosts

Writes out/angles.jsonl (per-hit) and out/angles_summary.json.
"""
import collections
import glob
import hashlib
import json
import re
from pathlib import Path
import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from mcp_paths import data_dir  # noqa: E402
from urllib.parse import urlparse, parse_qs

HERE = Path(__file__).resolve().parent
DATA = data_dir()
I = re.I

PAT = {
    "reply_branding": re.compile(
        r"\b(always |must )?(end|finish|close|conclude|sign off|append to|start|begin|prefix)\b[^.\n]{0,25}"
        r"\b(your |every |each |the )?(response|reply|answer|message)s?\b[^.\n]{0,20}\b(with|by)\b|"
        r"\bpowered by\b|\b(always|must)\s+(mention|credit|cite|attribute|include|link|show)\b[^.\n]{0,40}"
        r"\b(our|the)\s+(website|site|brand|company|name|homepage|logo|link)\b|"
        r"\b(include|add|show|display)\b[^.\n]{0,30}\b(call[- ]to[- ]action|cta|signup link|sign-up link|"
        r"upgrade link|promo(tional)? (code|link))\b", I),
    "upsell": re.compile(
        r"\b(suggest|recommend|offer|mention|encourage|prompt|nudge|invite)\b[^.\n]{0,40}\b(upgrad\w+|"
        r"premium|pro plan|paid plan|subscri\w+|buy(ing)? (more )?credits|top[- ]?up|higher tier)\b|"
        r"\bupsell\b|\bsister (service|product|site|server|tool)s?\b|\bcross[- ]?sell\b|"
        r"\bour other (products|services|tools|servers)\b", I),
    "agent_seo": re.compile(
        r"\b(the )?(best|#1|number one|leading|most (accurate|comprehensive|trusted|reliable|complete))\b"
        r"[^.\n]{0,40}\b(tool|server|mcp|source|api|provider|data|platform)\b|"
        r"\bbetter than\b[^.\n]{0,30}\b(web ?search|google|other|any|alternatives|chatgpt|training)\b|"
        r"\b(only|first)\s+(verified|official|government[- ]verified|authoritative|trusted)\b[^.\n]{0,30}"
        r"\b(source|tool|server|mcp|data)\b|\bprefer (this|these|us)\b|\bchoose (this|us)\b", I),
}
URL = re.compile(r"https?://[^\s\"'<>)\]}]+")
TRACK_KEYS = re.compile(r"^(utm_\w+|ref|refid|ref_id|referrer|src|source|aff|affid|aff_id|affiliate|"
                        r"tag|campaign|cid|clickid|gclid|via|partner|pid)$", I)
PII_PARAM = re.compile(r"(^|_)(email|phone|mobile|tel|zip|postcode|postal_code|full_?name|first_?name|"
                       r"last_?name|address|dob|birth|income|age)($|_)", I)
LEAD_CTX = re.compile(r"\b(partner|installer|agent|broker|lender|provider|advisor|sales team|"
                      r"we (will )?(share|pass|send|forward)|referral fee|lead|contact you|call you|"
                      r"get in touch|callback|quote)\b", I)


def results(d, method):
    for ex in d.get("exchanges", []):
        if ex.get("method") == method:
            r = (ex.get("response") or {}).get("result")
            if isinstance(r, dict):
                yield r


def texts(d, prompts_file):
    for r in results(d, "initialize"):
        if isinstance(r.get("instructions"), str):
            yield "instructions", None, r["instructions"]
    for r in results(d, "tools/list"):
        for t in r.get("tools") or []:
            if isinstance(t, dict) and isinstance(t.get("description"), str):
                yield "tool_description", t.get("name"), t["description"]
    if prompts_file.exists():
        for ex in json.load(open(prompts_file)).get("exchanges", []):
            r = (ex.get("response") or {}).get("result")
            if isinstance(r, dict):
                for m in r.get("messages") or []:
                    c = m.get("content") or {}
                    if isinstance(c.get("text"), str):
                        yield "prompt_message", ex["request"]["params"].get("name"), c["text"]


def main():
    out = open(HERE / "out" / "angles.jsonl", "w")
    servers = collections.defaultdict(set)
    fingerprints = collections.defaultdict(list)
    n_ok = 0
    for f in sorted(glob.glob(str(DATA / "*.json"))):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d.get("status") != "ok":
            continue
        n_ok += 1
        ep = d["endpoint"]
        host = urlparse(ep).hostname or ""
        for surface, where, text in texts(d, DATA / "prompts" / Path(f).name):
            for k, rx in PAT.items():
                for m in rx.finditer(text):
                    servers[k].add(ep)
                    out.write(json.dumps({"angle": k, "endpoint": ep, "surface": surface, "where": where,
                                          "match": m.group(0),
                                          "ctx": text[max(0, m.start() - 180): m.end() + 180]},
                                         ensure_ascii=False) + "\n")
            for u in URL.findall(text):
                try:
                    p = urlparse(u.rstrip(".,;"))
                except ValueError:
                    continue  # malformed URL text in someone's metadata
                keys = [k for k in parse_qs(p.query) if TRACK_KEYS.match(k)]
                if keys:
                    servers["tracking_url"].add(ep)
                    out.write(json.dumps({"angle": "tracking_url", "endpoint": ep, "surface": surface,
                                          "where": where, "url": u[:300], "keys": keys,
                                          "own_domain": (p.hostname or "").endswith(".".join(host.split(".")[-2:]))},
                                         ensure_ascii=False) + "\n")
        # lead generation: a tool taking contact PII whose description mentions handing it on
        for r in results(d, "tools/list"):
            for t in r.get("tools") or []:
                if not isinstance(t, dict):
                    continue
                props = list(((t.get("inputSchema") or {}).get("properties") or {}).keys())
                pii = [p for p in props if PII_PARAM.search(p)]
                desc = t.get("description") or ""
                if len([p for p in pii if re.search(r"email|phone|mobile|tel", p, I)]) and LEAD_CTX.search(desc):
                    servers["lead_gen"].add(ep)
                    out.write(json.dumps({"angle": "lead_gen", "endpoint": ep, "where": t.get("name"),
                                          "pii": pii, "ctx": desc[:400]}, ensure_ascii=False) + "\n")
        # clone clusters: same instructions + same sorted tool names on different hosts
        instr = next((r.get("instructions") or "" for r in results(d, "initialize")), "")
        names = sorted(t.get("name", "") for r in results(d, "tools/list")
                       for t in r.get("tools") or [] if isinstance(t, dict))
        if names:
            fp = hashlib.sha1(json.dumps([re.sub(r"\S+\.(de|com|io|app|dev)\b", "", instr)[:2000],
                                          names]).encode()).hexdigest()
            fingerprints[fp].append(ep)
    clusters = [v for v in fingerprints.values()
                if len({urlparse(e).hostname.split(".")[-2] for e in v}) >= 3]
    clusters.sort(key=len, reverse=True)
    for c in clusters:
        out.write(json.dumps({"angle": "clone_cluster", "size": len(c), "endpoints": c}) + "\n")
    summary = {"servers_ok": n_ok, **{k: len(v) for k, v in servers.items()},
               "clone_clusters(>=3 distinct domains)": len(clusters),
               "servers_in_clone_clusters": sum(len(c) for c in clusters)}
    json.dump(summary, open(HERE / "out" / "angles_summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
