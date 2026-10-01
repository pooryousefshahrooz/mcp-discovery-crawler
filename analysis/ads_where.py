#!/usr/bin/env python3
"""Where do ads live, which networks, and are the same ads repeated?

A. For the hand-labelled ad servers (ads_labels.json): which layer carries the
   ad signal (server instructions / tool description / input schema / output
   schema / prompt / resource / HTTP header) and how many tools per server.
B. Ad text already visible in discovery metadata: promo codes, discounts,
   explicit calls to action pointing at third parties.
C. The same promotional sentence on servers of different operators.
D. Ad networks, affiliate programs and retailers named by the ad servers.
"""
import collections
import glob
import json
import re
from pathlib import Path
import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from mcp_paths import data_dir  # noqa: E402
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
DATA = data_dir()
LABELS = json.load(open(HERE / "ads_labels.json"))
AD_SERVERS = {ep: role for role, eps in LABELS.items() if role != "neutrality_claim" for ep in eps}
I = re.I


def operator(ep):
    host = urlparse(ep).hostname or ""
    parts = host.split(".")
    return ".".join(parts[-3:]) if parts[-2] in ("co", "com", "org") and len(parts) > 2 else ".".join(parts[-2:])


def results(d, method):
    for ex in d.get("exchanges", []):
        if ex.get("method") == method:
            r = (ex.get("response") or {}).get("result")
            if isinstance(r, dict):
                yield r


def all_text(d, prompts_file):
    for r in results(d, "initialize"):
        if isinstance(r.get("instructions"), str):
            yield "server_instructions", None, r["instructions"]
    for r in results(d, "tools/list"):
        for t in r.get("tools") or []:
            if isinstance(t, dict) and isinstance(t.get("description"), str):
                yield "tool_description", t.get("name"), t["description"]
    for r in results(d, "resources/list"):
        for x in r.get("resources") or []:
            if isinstance(x, dict) and isinstance(x.get("description"), str):
                yield "resource_description", x.get("uri"), x["description"]
    if prompts_file.exists():
        for ex in json.load(open(prompts_file)).get("exchanges", []):
            r = (ex.get("response") or {}).get("result")
            if isinstance(r, dict):
                for m in r.get("messages") or []:
                    c = m.get("content") or {}
                    if isinstance(c.get("text"), str):
                        yield "prompt_text", ex["request"]["params"].get("name"), c["text"]


PROMO = re.compile(
    r"\b(\d{1,2}\s?%\s?(off|discount|rabatt)|promo(tion(al)?)?\s?code|coupon|discount code|use code|"
    r"free trial|sign up (at|now|free)|get started (at|free)|visit https?://|try (it )?(free|now)|"
    r"limited[- ]time|special offer|exclusive (deal|offer|discount))\b", I)
NETWORKS = re.compile(
    r"\b(amazon associates|amazon|ebay partner network|ebay|aliexpress|awin|shareasale|impact(\.com)?|"
    r"cj affiliate|rakuten|partnerize|skimlinks|sovrn|kraken|stripe|lulu ads|picoads|adoraads|"
    r"google ads|admob|booking\.com|expedia|ifood|rappi|uber[- ]eats|wix)\b", I)


def main():
    # ---- A: where the ad signal lives, from ads_candidates.jsonl hits
    surf_map = {"instructions": "server_instructions", "tool_description": "tool_description",
                "tool_name": "tool_description", "input_desc": "input_schema", "input_prop": "input_schema",
                "output_desc": "output_schema", "output_prop": "output_schema",
                "tool_meta_key": "tool__meta", "init_meta_key": "server__meta",
                "prompt_description": "prompt", "prompt_message": "prompt",
                "resource_description": "resource"}
    per_server = {}
    for line in open(HERE / "out" / "ads_candidates.jsonl"):
        c = json.loads(line)
        if c["endpoint"] not in AD_SERVERS:
            continue
        layers, tools = collections.Counter(), set()
        for flag in ("ad", "affiliate", "schema_ad"):
            for h in c["hits"].get(flag, []):
                layer = surf_map.get(h["surface"], h["surface"])
                layers[layer] += 1
                w = h.get("where")
                if w and h["surface"] not in ("instructions", "prompt_message", "prompt_description",
                                              "resource_description", "init_meta_key"):
                    tools.add(str(w).split(":")[0])
        per_server[c["endpoint"]] = {"role": AD_SERVERS[c["endpoint"]], "layers": layers,
                                     "ad_tools": len(tools), "n_tools": c["n_tools"]}
    # header-only signal (umesh-malik's x-agent-ad header)
    for f in glob.glob(str(DATA / "*.json")):
        d = json.load(open(f))
        if d["endpoint"] in AD_SERVERS:
            for ex in d.get("exchanges", []):
                if any(re.search(r"(^|-)ad(-|$)", k, I) for k in (ex.get("headers") or {})):
                    per_server.setdefault(d["endpoint"], {"role": AD_SERVERS[d["endpoint"]],
                                                          "layers": collections.Counter(),
                                                          "ad_tools": 0, "n_tools": 0})
                    per_server[d["endpoint"]]["layers"]["http_header"] += 1
                    break

    layer_servers = collections.Counter()
    for v in per_server.values():
        for layer in v["layers"]:
            layer_servers[layer] += 1
    only_one = collections.Counter(next(iter(v["layers"])) for v in per_server.values() if len(v["layers"]) == 1)
    print(f"A. ad servers with located signals: {len(per_server)} (of {len(AD_SERVERS)} labelled)")
    print("   servers per layer:", dict(layer_servers.most_common()))
    print("   servers whose ad signal sits in ONE layer only:", dict(only_one))
    tot_ad_tools = sum(v["ad_tools"] for v in per_server.values())
    tot_tools = sum(v["n_tools"] for v in per_server.values())
    print(f"   tools carrying an ad signal: {tot_ad_tools} of {tot_tools} tools on these servers")
    top = sorted(per_server.items(), key=lambda kv: -kv[1]["ad_tools"])[:10]
    for ep, v in top:
        print(f"     {v['ad_tools']:3}/{v['n_tools']:<4} {v['role']:26} {ep}")

    # ---- B/C/D over the whole corpus
    promo_hits, sent_ops = [], collections.defaultdict(set)
    networks = collections.defaultdict(set)
    for f in sorted(glob.glob(str(DATA / "*.json"))):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d.get("status") != "ok":
            continue
        ep = d["endpoint"]
        for layer, where, text in all_text(d, DATA / "prompts" / Path(f).name):
            for m in PROMO.finditer(text):
                promo_hits.append({"endpoint": ep, "layer": layer, "where": where, "match": m.group(0),
                                   "ctx": text[max(0, m.start() - 150): m.end() + 150]})
            for s in re.split(r"(?<=[.!?])\s+|\n+", text):
                s2 = re.sub(r"\s+", " ", s.strip().lower())
                if 40 <= len(s2) <= 300 and (PROMO.search(s2) or re.search(
                        r"sponsor|affiliate|promot|referral|powered by|commission", s2)):
                    sent_ops[s2].add(operator(ep))
            if ep in AD_SERVERS:
                for m in NETWORKS.finditer(text):
                    networks[m.group(0).lower()].add(ep)
    with open(HERE / "out" / "promo_hits.jsonl", "w") as out:
        for h in promo_hits:
            out.write(json.dumps(h, ensure_ascii=False) + "\n")
    print(f"\nB. promo phrases in metadata: {len(promo_hits)} hits on "
          f"{len({h['endpoint'] for h in promo_hits})} servers; by layer:",
          dict(collections.Counter(h["layer"] for h in promo_hits)))
    rep = sorted(((len(v), s, sorted(v)) for s, v in sent_ops.items() if len(v) >= 2), reverse=True)
    print(f"\nC. promotional sentences repeated across >=2 operators: {len(rep)}")
    for n, s, ops in rep[:15]:
        print(f"   {n} operators: {s[:150]!r}  {ops[:5]}")
    print("\nD. networks / programs / retailers named by ad servers:")
    for k, v in sorted(networks.items(), key=lambda kv: -len(kv[1])):
        print(f"   {k:22} {len(v)} servers")


if __name__ == "__main__":
    main()
