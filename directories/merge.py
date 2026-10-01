#!/usr/bin/env python3
"""Merge per-directory listings into one deduplicated endpoint list.

Reads directories/raw/*.jsonl (from collect.py) and writes:
  directories/listings_all.csv   one row per listing (all sources, incl. listings without an endpoint)
  directories/endpoints.csv      one row per unique remote endpoint, with the directories that list it;
                                 has an `endpoint` column so it can be fed straight to discover.py
Also prints a per-source summary table.
"""
import collections
import csv
import glob
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

HERE = Path(__file__).resolve().parent
BAD = re.compile(r"[{}<>]|your[-_]|example\.com|localhost|127\.0\.0\.1|0\.0\.0\.0|\$\{|xxx", re.I)


def norm(url):
    """Canonical form for dedup: lowercase scheme/host, drop fragment and trailing slash."""
    try:
        p = urlsplit(url.strip())
    except ValueError:
        return None
    if p.scheme not in ("http", "https") or not p.hostname or BAD.search(url):
        return None
    path = p.path.rstrip("/") or ""
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), path, p.query, ""))


def main():
    rows = []
    for f in sorted(glob.glob(str(HERE / "raw" / "*.jsonl"))):
        for line in open(f):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    with open(HERE / "listings_all.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "server_name", "listing_url", "endpoint", "transport", "auth", "extra"])
        for r in rows:
            w.writerow([r["source"], r["server_name"], r["listing_url"], r["endpoint"], r["transport"], r["auth"],
                        json.dumps(r.get("extra", {}), ensure_ascii=False)])

    eps = collections.OrderedDict()
    per = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        s = r["source"]
        per[s]["listings"] += 1
        if r.get("extra", {}).get("error") or r.get("extra", {}).get("parse_error"):
            per[s]["fetch_or_parse_errors"] += 1
        n = norm(r["endpoint"]) if r["endpoint"] else None
        if not n:
            continue
        per[s]["with_remote_endpoint"] += 1
        e = eps.setdefault(n, {"endpoint": n, "sources": set(), "names": set(), "listing_urls": set(),
                               "transports": set(), "auth": set()})
        e["sources"].add(s)
        if r["server_name"]:
            e["names"].add(r["server_name"][:80])
        e["listing_urls"].add(r["listing_url"])
        if r["transport"]:
            e["transports"].add(r["transport"])
        if r["auth"]:
            e["auth"].add(f"{s}: {r['auth']}")
    for e in eps.values():
        for s in e["sources"]:
            per[s]["unique_endpoints"] += 1
            if len(e["sources"]) == 1:
                per[s]["only_in_this_source"] += 1

    with open(HERE / "endpoints.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["endpoint", "n_sources", "sources", "server_names", "transports", "auth_stated", "listing_urls"])
        for e in eps.values():
            w.writerow([e["endpoint"], len(e["sources"]), ";".join(sorted(e["sources"])), " | ".join(sorted(e["names"]))[:300],
                        ";".join(sorted(e["transports"])), " | ".join(sorted(e["auth"]))[:300],
                        " ".join(sorted(e["listing_urls"]))[:600]])

    cols = ["listings", "with_remote_endpoint", "unique_endpoints", "only_in_this_source", "fetch_or_parse_errors"]
    print(f"{'source':14}" + "".join(f"{c:>24}" for c in cols))
    for s in sorted(per):
        print(f"{s:14}" + "".join(f"{per[s][c]:>24}" for c in cols))
    multi = sum(1 for e in eps.values() if len(e["sources"]) > 1)
    print(f"\nunique endpoints overall: {len(eps)}  (listed in >1 directory: {multi})")


if __name__ == "__main__":
    main()
