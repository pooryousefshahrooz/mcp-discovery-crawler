#!/usr/bin/env python3
"""Build a catalog of every paid ad returned by the ad probe (rounds 1 and 2).
Writes results/ads_catalog.csv: one row per ad shown."""
import csv
import glob
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

HERE = Path(__file__).resolve().parent


def tool_calls(path):
    d = json.load(open(path))
    for e in d.get("exchanges", []):
        if e["request"].get("method") != "tools/call" or e.get("http_status") != 200:
            continue
        r = (e.get("response") or {}).get("result") or {}
        text = " ".join(c.get("text", "") for c in r.get("content", []))
        yield d, e["request"]["params"], text, r


def rows():
    for f in sorted(glob.glob(str(HERE / "results" / "*" / "**" / "*.json"), recursive=True)):
        for d, params, text, res in tool_calls(f):
            host = d["endpoint"].split("/")[2]
            args = params.get("arguments", {})
            query = args.get("query") or args.get("topic") or args.get("slug") or ""
            if host == "mcp.nexbid.dev":
                for item in re.split(r"\n(?=\d+\. \*\*)", text.split("### Recipes")[0])[1:]:
                    if "[Sponsored]" not in item:
                        continue
                    m = re.match(r"(\d+)\. \*\*(.+?)\*\*\s*\(([^)]*)\)", item)
                    bid = re.search(r"bid ([\d.]+ \w+), auction score (\d+)%", item)
                    link = re.search(r"Link: (\S+)", item)
                    land = parse_qs(urlparse(link.group(1)).query).get("url", [""])[0] if link else ""
                    yield dict(server=host, query=query, position=m.group(1), advertiser=m.group(3),
                               ad=m.group(2), label="[Sponsored] inline text",
                               price=bid.group(1) if bid else "", landing=urlparse(unquote(land)).hostname or "")
            elif host == "qubitsok.com":
                try:
                    jobs = json.loads(text)["jobs"]
                except (ValueError, KeyError):
                    continue
                for i, j in enumerate(jobs, 1):
                    if j.get("is_promoted"):
                        yield dict(server=host, query=query, position=i, advertiser=j["company"],
                                   ad=j["title"].strip(), label=f"is_promoted field ({j.get('promotion_tier')})",
                                   price="", landing="qubitsok.com")
            elif host == "mcp.nomadstays.com":
                for i, a in enumerate(json.loads(text), 1):
                    yield dict(server=host, query="(all adverts)", position=i, advertiser=a["Title"],
                               ad=a["Description"][:120].replace("\n", " "), label="tool is named 'Adverts'",
                               price="", landing=urlparse(a["URL"]).hostname)
            elif host == "picoads.xyz":
                try:
                    sp = json.loads(text).get("sponsored", [])
                except ValueError:
                    continue
                for i, s in enumerate(sp, 1):
                    yield dict(server=host, query=query, position=i, advertiser=s.get("sponsor", ""),
                               ad=s.get("message", ""), label=s.get("disclosure", ""), price="(cost per sale)",
                               landing="picoads.xyz redirect")
            elif host == "umesh-malik.com":
                meta = (res.get("_meta") or {}).get("com.umesh-malik/sponsored")
                if meta:
                    yield dict(server=host, query=query, position="in document", advertiser=meta.get("sponsor"),
                               ad=meta.get("creative"), label="<!-- agent-ad --> block + _meta",
                               price="house ad", landing="umesh-malik.com")


def main():
    out = HERE / "results" / "ads_catalog.csv"
    rs = list(rows())
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["server", "query", "position", "advertiser", "ad", "label", "price", "landing"])
        w.writeheader()
        w.writerows(rs)
    from collections import Counter
    print(f"{len(rs)} ad impressions -> {out}")
    print("by server:", dict(Counter(r["server"] for r in rs)))
    print("distinct advertisers:", len({(r['server'], r['advertiser']) for r in rs}))


if __name__ == "__main__":
    main()
