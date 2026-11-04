#!/usr/bin/env python3
"""Hand codes for signatures first seen in the live ad-metadata probe (not in the v2 provenance
study). Rules follow analysis/ad_provenance/CODEBOOK.md; each rule cites its rationale.
Writes coding/new_signature_codes.json. Re-run after M1 if new signatures appear.

  python3 analysis/ad_metadata/coding/code_new_signatures.py
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNC = HERE.parent / "out" / "uncoded_signatures.csv"
OUT = HERE / "new_signature_codes.json"

# explicit per-signature decisions (checked against the raw example)
BY_SIG = {
    "78b8bef78e84": ("not_ad", "n/a", "disclosure text on an empty result (deals: []) - no ad item"),
    "fce33cfab476": ("confirmed_ad", "third_party_content", "Walmart 'Sponsored' product label inside a scraped page"),
    "230fcbd1829c": ("confirmed_ad", "operator", "per-offer 'Affiliate link. padel.how may earn a commission'"),
    "ab776721400a": ("confirmed_ad", "operator", "per-offer 'Affiliate link. padel.how may earn a commission'"),
    "e94be6311c2f": ("commercial_other", "operator", "'Some links ... are affiliate links' - no identifiable ad item"),
    "6b97eeeaa874": ("confirmed_ad", "operator", "states the returned signup links are referral links (coinrebate referral ads, v2 confirmed)"),
    "0b708aca0264": ("confirmed_ad", "operator", "operator /go/<exchange> referral redirect with fee discount"),
    "ce0bfec63d4d": ("commercial_other", "n/a", "Eventbrite aff=oddtdtcreator is the event creator's tag (source: discovery), not gigstamp's"),
    "95e73ce11978": ("confirmed_ad", "operator", "wem3 /api/go redirect wrapping a retailer link with clickref=wem-*"),
    "fa9e815510f8": ("promotional", "operator", "wem3 /shop redirect with UTM only (host-level v2 code: promotional)"),
}


# retrieval tools whose ads sit inside retrieved third-party content (web pages, social posts)
THIRD_PARTY = {"mcp.firecrawl.dev", "bluesky.caseyjhand.com", "socialbridge-mcp.vercel.app"}


def rule(x):
    h, kind, sigs = x["host"], x["kind"], x["signals"]
    if h == "tulugar.com" and kind == "label" and "paid placement" in x["example"].lower():
        return ("confirmed_ad", "operator", "listing labelled 'FEATURED (paid placement, labeled Destacado)'")
    if h in THIRD_PARTY:
        if sigs == "redirect_path":
            return ("not_ad", "n/a", "redirect path only inside scraped page (v2 code for this class: not_ad)")
        return ("confirmed_ad", "third_party_content", "affiliate link / sponsored label inside retrieved third-party content (v2: Firecrawl/WSJ case)")
    if h.startswith("wo") and h.endswith(".de") and sigs == "attrib_utm":
        return ("not_ad", "n/a", "link to the operator's own guide/brand page with UTM only")
    if kind in ("url", "nested") and sigs != "attrib_utm":
        return ("confirmed_ad", "operator",
                "same affiliate/referral mechanism as the server's v2-confirmed ads (new link host/path)")
    return None


def main():
    codes = {}
    for x in csv.DictReader(open(UNC)):
        c = BY_SIG.get(x["sig"]) or rule(x)
        if not c:
            raise SystemExit(f"no rule for {x['sig']} {x['host']} {x['kind']} {x['signals']}")
        codes[x["sig"]] = {"status": c[0], "origin": c[1], "note": c[2], "host": x["host"], "tool": x["tool"],
                           "kind": x["kind"], "signals": x["signals"], "url_host": x["url_host"]}
    old = json.load(open(OUT)) if OUT.exists() else {}
    old.update(codes)
    json.dump(old, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"coded {len(codes)} (total {len(old)})")


if __name__ == "__main__":
    main()
