#!/usr/bin/env python3
"""Detect ads in probe tool outputs (offline).

Usage: python3 ad_probe/detect_ads.py [RESULTS_GLOB]
       default glob: ad_probe/results/v2/*/*.jsonl

For every tool call, flags:
  paid      paid-placement markers ([Sponsored], is_sponsored/is_promoted true,
            agent-ad blocks, "Sponsored via", promoted listing, ad-network names)
  affiliate affiliate links (known parameters / networks) or affiliate disclosures
Writes ad_probe/results/detections.csv (one row per call) and prints per-server
and overall rates.
"""
import collections
import csv
import glob
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
PAID = re.compile(
    r"\[sponsored\]|\(sponsored\)|\"(is_)?sponsored\"\s*:\s*true|\"is_promoted\"\s*:\s*true|<!--\s*agent-ad\b|"
    r"sponsored via|promoted listing|\"promotion_tier\"\s*:\s*\"|\"ad_id\"|\"adId\"|(?<!no )(?<!never )\bpaid placement\b(?! never)(?! does not)|"
    r"\bsponsored (result|product|listing|content|recommendation)s?\b|https?://[^\s\"']*nomadstays\.com/ad/\d+", re.I)
NETWORK = re.compile(r"agentic[- ]ads|adgentek|agentvine|chatads|trygravity|koahlabs|picoads|getlulu|adoraads", re.I)
TRACKER = re.compile(r"https?://[^\s\"'<>)\]]*(?:/track/click|/api/go/|/go/|/out\?|/rs/|redirect\?)[^\s\"'<>)\]]*", re.I)
AFF_URL = re.compile(
    r"https?://[^\s\"'<>)\]]*(?:[?&](?:tag|campid|aff|aff_id|affid|affiliate|affiliate_id|refid|irclickid|"
    r"clickid|subid)=|utm_medium=affiliate|evyy\.net|awin1\.com|dpbolvw\.net|anrdoezrs\.net|jdoqocy\.com|"
    r"tkqlhce\.com|kqzyfj\.com|shareasale\.com/r\.cfm|pntra\.com|go\.skimresources|click\.linksynergy|"
    r"s\.click\.aliexpress|rover\.ebay|amzn\.to)[^\s\"'<>)\]]*", re.I)
AFF_TEXT = re.compile(r"affiliate[- ]link|affiliate commission|kann affiliate|(?:erh[aä]e?lt|eine|ggf\.?) provision|we may earn a commission|"
                      r"earn a commission", re.I)


def texts(rec):
    r = (rec.get("response") or {}).get("result") or {}
    parts = [c.get("text", "") for c in r.get("content", []) if isinstance(c, dict)]
    parts.append(json.dumps(r.get("structuredContent") or {}, ensure_ascii=False))
    parts.append(json.dumps(r.get("_meta") or {}, ensure_ascii=False))
    return " ".join(parts).replace('\\"', '"')


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else str(HERE / "results" / "v2" / "*" / "*.jsonl")
    rows = []
    for f in sorted(glob.glob(pattern)):
        for line in open(f):
            rec = json.loads(line)
            ok = rec.get("http_status") == 200 and "result" in (rec.get("response") or {}) \
                and not ((rec.get("response") or {}).get("result") or {}).get("isError")
            t = texts(rec) if ok else ""
            paid = sorted({m.group(0).lower()[:40] for m in PAID.finditer(t)})
            aff_urls = AFF_URL.findall(t)
            # ignore explicit negative self-reports such as "affiliate_links_in_this_response": false
            t_aff = re.sub(r'"affiliate_links_in_this_response"\s*:\s*false[^}]*', " ", t)
            aff = bool(aff_urls) or bool(AFF_TEXT.search(t_aff))
            tracked = bool(TRACKER.search(t))
            network = sorted({m.group(0).lower() for m in NETWORK.finditer(t)})
            rows.append({"server": urlparse(rec["endpoint"]).hostname, "tool": rec["tool"],
                         "arguments": json.dumps(rec["arguments"], ensure_ascii=False), "ok": ok,
                         "paid": bool(paid), "affiliate": aff, "click_tracked": tracked,
                         "mentions_network": "; ".join(network), "paid_markers": "; ".join(paid)[:200],
                         "affiliate_hosts": "; ".join(sorted({urlparse(u).hostname or "" for u in aff_urls}))[:200]})
    out = HERE / "results" / "detections.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["server"])
        w.writeheader()
        w.writerows(rows)
    per = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        c = per[r["server"]]
        c["calls"] += 1
        c["ok"] += r["ok"]
        c["paid"] += r["paid"]
        c["affiliate"] += r["affiliate"]
        c["tracked"] += r["click_tracked"]
    srv_ok = [s for s, c in per.items() if c["ok"]]
    srv_paid = [s for s in srv_ok if per[s]["paid"]]
    srv_aff = [s for s in srv_ok if per[s]["affiliate"]]
    srv_any = set(srv_paid) | set(srv_aff)
    okcalls = sum(r["ok"] for r in rows)
    print(f"calls: {len(rows)} (successful {okcalls}) | servers probed: {len(per)} (with >=1 successful call: {len(srv_ok)})")
    pct = lambda a, b: f"{a}/{b} ({100 * a / b:.1f}%)" if b else "0/0"
    print("servers serving paid placements:", pct(len(srv_paid), len(srv_ok)))
    print("servers serving affiliate links:  ", pct(len(srv_aff), len(srv_ok)))
    print("servers serving either:           ", pct(len(srv_any), len(srv_ok)))
    print("successful calls with a paid placement:", pct(sum(r["paid"] for r in rows), okcalls))
    print("successful calls with affiliate links: ", pct(sum(r["affiliate"] for r in rows), okcalls))
    print("servers routing links through click trackers:", pct(sum(1 for s in srv_ok if per[s]["tracked"]), len(srv_ok)))
    print("\nper server (servers with any ad):")
    for s in sorted(srv_any, key=lambda s: -(per[s]["paid"] + per[s]["affiliate"])):
        c = per[s]
        print(f"  {s:42} ok={c['ok']:3} paid={c['paid']:3} affiliate={c['affiliate']:3}")
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
