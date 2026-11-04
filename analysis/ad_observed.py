#!/usr/bin/env python3
"""Canonical definition of the OBSERVED ad-serving servers and their ad responses.

Shared by exp1-exp4 so every experiment uses the same denominator. A server is an
"observed ad server" only if it actually RETURNED at least one ad in a tool result,
i.e. a real paid placement or tracking/affiliate link, NOT merely a declared-but-empty
sponsored slot, a policy description, or an ad-related word in documentation.

Confirmed false positives excluded by this rule (hand-verified 2026-10-11):
  bagsthatpay.com, issafu.com, wenreceipts.com   -> {"label":"Sponsored","placements":[]} (empty)
  agorean.com                                     -> "promoted-slot" is a docs topic name
  www.gamedevoutsourcing.com                      -> "Paid listings ... first" is a policy string
"""
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "ad_probe" / "results"
DIRS = [RESULTS / "full" / "full-2026-10-09", RESULTS / "full" / "qbattery",
        RESULTS / "v2" / "ad-networks"]
# early one-file-per-call probe runs (.json with an "exchanges" list)
JSON_DIRS = [RESULTS / "2026-09-30", RESULTS / "2026-09-30" / "round2"]

# A REAL served ad: a non-empty sponsored placement, a tracking/redirect click link, an
# affiliate tag/param, an agent/UTM-tagged link, or an inline [Sponsored] marker on an item.
REAL_AD = re.compile(
    r'"placements"\s*:\s*\[\s*\{'                        # non-empty sponsored placements
    r'|is_sponsored"?\s*:\s*true|is_promoted"?\s*:\s*true'
    r'|promotion_tier"\s*:\s*"[^"]+'
    r'|"sponsored"\s*:\s*\[\s*\{'
    r'|\[sponsored\]\s*\S'                                # inline [Sponsored] on an item
    r'|/track/click'
    r'|\?tag=[a-z0-9]+-2\d'                                 # Amazon associate tag
    r'|utm_(source|medium)=[^&\s"]+'                         # UTM-tagged link
    r'|/go/[A-Za-z0-9%]|/aff/[A-Za-z0-9]'                     # redirect with payload
    r'|affiliate[_ -]?url"\s*:\s*"https?'                   # affiliate_url with a value
    r'|As an Amazon Associate'
    r'|affiliate links?[^.\n]{0,60}(commission|earn|Associates)'  # affiliate + commission disclosure
    r'|sponsored[ _-]?by\s+\w', re.I)

# never count these: declared-but-empty, explicitly-not-sponsored, or error/no-result responses
_FALSE = re.compile(r'"placements"\s*:\s*\[\s*\]|is_sponsored"?\s*:\s*false|'
                    r'"sponsored"\s*:\s*\[\s*\]', re.I)


def result_text(r):
    res = (r.get("response") or {}).get("result") or {}
    return "".join(c.get("text", "") for c in res.get("content") or [] if isinstance(c, dict)) or json.dumps(res, ensure_ascii=False)


import re as _re


def _exchanges_text(d):
    out = []
    for e in d.get("exchanges", []):
        res = (e.get("response") or {}).get("result") or {}
        t = "".join(c.get("text", "") for c in res.get("content") or [] if isinstance(c, dict)) or json.dumps(res, ensure_ascii=False)
        out.append(t)
    return "\n".join(out)


def observed_ad_servers():
    """Return {host: [ad-bearing response texts]} for every server that served a real ad,
    across all tool-call probe runs (jsonl per-call and early per-file .json)."""
    out = {}
    for D in DIRS:
        for f in glob.glob(str(D / "*.jsonl")):
            host = Path(f).name[:-6]
            for line in open(f):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                t = result_text(r)
                if REAL_AD.search(t):
                    out.setdefault(host, []).append((r.get("arguments", {}), t))
    for D in JSON_DIRS:
        for f in glob.glob(str(D / "*.json")):
            host = _re.sub(r"^\d+_", "", Path(f).stem)
            try:
                d = json.load(open(f))
            except (ValueError, OSError):
                continue
            t = _exchanges_text(d)
            if REAL_AD.search(t):
                out.setdefault(host, []).append((d.get("arguments", {}), t))
    return out


if __name__ == "__main__":
    srv = observed_ad_servers()
    print(f"canonical observed ad-serving servers: {len(srv)}")
    for h in sorted(srv):
        print(f"  {h:34} {len(srv[h])} ad responses")
