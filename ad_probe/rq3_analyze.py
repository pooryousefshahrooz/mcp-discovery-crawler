#!/usr/bin/env python3
"""RQ3 analysis: query-targeting of delivered ads.

Reads results/rq3_targeting/*.jsonl (raw live responses), extracts the set of
AD IDENTITIES per response, and computes per server:
  within-query Jaccard  = similarity of ads across repeats of the SAME query
  across-query Jaccard  = similarity of ads across DIFFERENT queries
  targeting gap         = within - across   (positive => query-dependent ads)
plus per-(server,query) ad frequency. Aggregates with a hierarchical bootstrap
(resample servers, then reps) for 95% CIs, and renders fig_query_targeting.{pdf,png}.

Ad identity = normalized commercial item:
  * explicit sponsored/promoted items (is_sponsored / is_promoted / [Sponsored]) -> name/id
  * affiliate / tracking / redirect links -> final destination host+path (tracking params
    dropped; a destination hidden in url=/u= is decoded). Plain non-commercial links ignored.
"""
import csv
import glob
import itertools
import json
import random
import re
import statistics as st
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

HERE = Path(__file__).resolve().parent
FIGDIR = HERE.parent / "analysis" / "figs"
CATEGORIES = ["electronics", "travel", "clothing", "neutral"]  # overwritten from data in main()

URL = re.compile(r'https?://[^\s"\'<>)\]}]+', re.I)
# STRONG affiliate/paid signals only. NOT bare utm: some servers (e.g. nexbid) put a
# tracking redirect on every result, organic included, so utm alone is not an ad.
AFFIL = re.compile(
    r'[?&]tag=\w+-2\d'                                   # amazon associates tag
    r'|/aff/|/affiliate|affiliate_url'
    r'|\.evyy\.net|\.sjv\.io|\.pxf\.io|prf\.hn|ojrq\.net'  # impact/partnerize networks
    r'|linksynergy|shareasale|dpbolvw|anrdoezrs|kqzyfj|tkqlhce'  # rakuten/cj networks
    r'|awin1\.com|go\.redirectingat|skimresources|/go/offer', re.I)
DEST_PARAM = ("url", "u", "dest", "destination", "target", "to", "r", "link")


def reg_domain(host):
    parts = (host or "").split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else (host or "")


def norm_link(raw):
    """Normalized destination identity: decode a hidden dest param, drop tracking query."""
    raw = raw.rstrip('.,);')
    try:
        p = urlparse(raw)
    except ValueError:
        return None
    q = parse_qs(p.query)
    for k in DEST_PARAM:
        if k in q and q[k] and q[k][0].startswith("http"):
            return norm_link(unquote(q[k][0]))
    host = (p.hostname or "").lower()
    path = re.sub(r'/+$', '', p.path or "")
    return f"{host}{path}" if host else None


def extract_ad_identities(text):
    """Return a set of ad identities present in one response text."""
    ids = set()
    if not text:
        return ids
    # 1) structured JSON sponsored/promoted items
    try:
        obj = json.loads(text)
        stack = [obj]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                is_ad = any(x.get(k) is True for k in
                            ("is_sponsored", "is_promoted", "sponsored", "promoted", "is_ad"))
                if is_ad:
                    key = x.get("id") or x.get("title") or x.get("name") or x.get("company") or ""
                    if key:
                        ids.add(f"item::{str(key)[:120]}")
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
    except ValueError:
        pass
    # 2) inline [Sponsored] markers in markdown. Work LINE-BY-LINE: the paid tag and the
    # bolded item name sit on the same line (`N. **NAME** (brand) **[Sponsored]**`), so take
    # the first bold on that line. Line-level avoids mis-attributing an unnumbered sub-item.
    for ln in text.splitlines():
        if re.search(r'\[sponsored\]|\[promoted\]|\[\s*ad\s*\]|\[anzeige\]', ln, re.I):
            m = re.search(r'\*\*(.+?)\*\*', ln)
            if m and not re.fullmatch(r'\[?sponsored\]?', m.group(1).strip(), re.I):
                ids.add(f"item::{m.group(1).strip()[:120]}")
    # 3) affiliate / tracking / redirect links -> normalized destination
    for m in URL.finditer(text):
        raw = m.group(0)
        if AFFIL.search(raw):
            nl = norm_link(raw)
            if nl:
                ids.add(f"link::{nl}")
    return ids


def jaccard(a, b):
    if not a and not b:
        return None
    u = a | b
    return len(a & b) / len(u) if u else None


def load(indir):
    """host -> category -> list of (rep, ad_identity_set) for responses with >=1 ad."""
    data = defaultdict(lambda: defaultdict(list))
    adrows = []
    for f in sorted(glob.glob(str(indir / "*.jsonl"))):
        host = Path(f).stem
        for line in open(f):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("http") != 200:
                continue
            ids = extract_ad_identities(r.get("text", ""))
            data[host][r["category"]].append((r["rep"], ids))
            for idv in ids:
                adrows.append({"host": host, "category": r["category"], "query": r.get("query"),
                               "rep": r["rep"], "ad_identity": idv})
    return data, adrows


def server_metrics(cat_map):
    """within/across Jaccard and per-cat ad frequency for one server."""
    # ad frequency per category
    freq = {}
    for cat in CATEGORIES:
        runs = cat_map.get(cat, [])
        freq[cat] = (sum(1 for _, ids in runs if ids) / len(runs)) if runs else None
    # within-query: pairwise Jaccard among ad-bearing reps of the same category
    within = []
    for cat in CATEGORIES:
        sets = [ids for _, ids in cat_map.get(cat, []) if ids]
        for a, b in itertools.combinations(sets, 2):
            j = jaccard(a, b)
            if j is not None:
                within.append(j)
    # across-query: pairwise Jaccard among ad-bearing reps of different categories
    across = []
    cats_present = [c for c in CATEGORIES if any(ids for _, ids in cat_map.get(c, []))]
    for c1, c2 in itertools.combinations(cats_present, 2):
        s1 = [ids for _, ids in cat_map[c1] if ids]
        s2 = [ids for _, ids in cat_map[c2] if ids]
        for a in s1:
            for b in s2:
                j = jaccard(a, b)
                if j is not None:
                    across.append(j)
    return {
        "within": st.mean(within) if within else None,
        "across": st.mean(across) if across else None,
        "n_within_pairs": len(within), "n_across_pairs": len(across),
        "freq": freq,
        "ad_cats": len(cats_present),
    }


def hierarchical_bootstrap(per_server_runs, iters=2000, seed=1):
    """per_server_runs: list of cat_map dicts (only servers usable for across).
    Resample servers w/ replacement, then reps within each category, recompute aggregate."""
    rng = random.Random(seed)
    boot_within, boot_across, boot_gap = [], [], []
    servers = per_server_runs
    for _ in range(iters):
        samp = [servers[rng.randrange(len(servers))] for _ in servers]
        w_all, a_all = [], []
        for cat_map in samp:
            rs = {c: [cat_map[c][rng.randrange(len(cat_map[c]))] for _ in cat_map[c]]
                  for c in cat_map if cat_map[c]}
            m = server_metrics(rs)
            if m["within"] is not None:
                w_all.append(m["within"])
            if m["across"] is not None:
                a_all.append(m["across"])
        if w_all and a_all:
            boot_within.append(st.mean(w_all))
            boot_across.append(st.mean(a_all))
            boot_gap.append(st.mean(w_all) - st.mean(a_all))

    def ci(xs):
        xs = sorted(xs)
        lo = xs[int(0.025 * len(xs))]
        hi = xs[int(0.975 * len(xs))]
        return st.mean(xs), lo, hi
    return ci(boot_within), ci(boot_across), ci(boot_gap)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", default="rq3_targeting", help="subdir under ad_probe/results/")
    ap.add_argument("--tag", default="", help="suffix for output files, e.g. _domain")
    ap.add_argument("--exclude", default="qubitsok.com",
                    help="comma-separated hosts to drop from analysis/plot")
    a = ap.parse_args()
    indir = HERE / "results" / a.indir
    excluded = {h for h in a.exclude.split(",") if h}
    global CATEGORIES, OUTCSV, ADCSV
    OUTCSV = HERE / "results" / f"rq3_metrics{a.tag}.csv"
    ADCSV = HERE / "results" / f"rq3_ads{a.tag}.csv"

    data, adrows = load(indir)
    for h in excluded:
        data.pop(h, None)
    adrows = [r for r in adrows if r["host"] not in excluded]
    if excluded:
        print(f"excluded from analysis: {sorted(excluded)}\n")
    # auto-detect the category set actually present in the data
    cats = sorted({c for h in data for c in data[h]})
    if cats:
        CATEGORIES = cats
    print(f"input: {indir}\ncategories: {CATEGORIES}\n")
    FIGDIR.mkdir(parents=True, exist_ok=True)

    # per-server metrics
    rows = []
    usable = []  # servers with ads in >=2 categories (across computable)
    for host in sorted(data):
        m = server_metrics(data[host])
        row = {"host": host, "within": m["within"], "across": m["across"],
               "n_within_pairs": m["n_within_pairs"], "n_across_pairs": m["n_across_pairs"],
               "ad_categories": m["ad_cats"]}
        for c in CATEGORIES:
            row[f"adfreq_{c}"] = m["freq"][c]
        row["targeting_gap"] = (m["within"] - m["across"]) if (m["within"] is not None and m["across"] is not None) else None
        rows.append(row)
        if m["ad_cats"] >= 2 and m["within"] is not None and m["across"] is not None:
            usable.append(data[host])

    with open(OUTCSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    with open(ADCSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["host", "category", "query", "rep", "ad_identity"])
        w.writeheader(); w.writerows(adrows)

    serving = [r for r in rows if any((r[f"adfreq_{c}"] or 0) > 0 for c in CATEGORIES)]
    plot_rows = [r for r in rows if r["targeting_gap"] is not None]
    print(f"servers probed:                {len(rows)}")
    print(f"servers that served >=1 ad:    {len(serving)}")
    print(f"servers usable for targeting:  {len(plot_rows)} (ads in >=2 queries)")
    print()
    print(f"{'host':40} {'within':>7} {'across':>7} {'gap':>7}  adcats")
    for r in sorted(plot_rows, key=lambda x: -(x['targeting_gap'])):
        print(f"{r['host']:40} {r['within']:7.3f} {r['across']:7.3f} {r['targeting_gap']:7.3f}  {r['ad_categories']}")

    if usable:
        (wm, wlo, whi), (am, alo, ahi), (gm, glo, ghi) = hierarchical_bootstrap(usable)
        print(f"\nAGGREGATE (hierarchical bootstrap, {len(usable)} servers):")
        print(f"  within-query Jaccard: {wm:.3f}  [{wlo:.3f}, {whi:.3f}]")
        print(f"  across-query Jaccard: {am:.3f}  [{alo:.3f}, {ahi:.3f}]")
        print(f"  targeting gap:        {gm:.3f}  [{glo:.3f}, {ghi:.3f}]")
        make_figure(plot_rows, (wm, wlo, whi), (am, alo, ahi), a.tag)
    else:
        print("\nNo servers usable for targeting-gap (need ads in >=2 query categories).")
    print(f"\nmetrics -> {OUTCSV}\nads -> {ADCSV}")


def make_figure(plot_rows, within_ci, across_ci, tag=""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    plot_rows = sorted(plot_rows, key=lambda r: r["targeting_gap"])
    n = len(plot_rows)
    C_WITHIN, C_ACROSS = "#1b4965", "#e07a5f"

    fig, ax = plt.subplots(figsize=(7.2, max(3.2, 0.26 * n + 1.6)))
    ys = list(range(n))
    for y, r in zip(ys, plot_rows):
        ax.plot([r["across"], r["within"]], [y, y], color="#999999", lw=0.8, zorder=1)
        ax.scatter(r["across"], y, s=34, color=C_ACROSS, zorder=3, edgecolor="white", linewidth=0.5)
        ax.scatter(r["within"], y, s=34, color=C_WITHIN, zorder=3, edgecolor="white", linewidth=0.5)
        ax.text(1.11, y, f"{r['targeting_gap']:.2f}", fontsize=6.5, va="center", ha="right",
                color="#333333")
    labels = [r["host"].replace(".workers.dev", "").replace("-production.up.railway.app", "")[:28] for r in plot_rows]
    ax.set_yticks(ys); ax.set_yticklabels(labels, fontsize=7)
    ax.set_ylim(-1, n + 2.5)

    # aggregate band at the top
    yagg = n + 1.2
    ax.plot([across_ci[0], within_ci[0]], [yagg, yagg], color="#333", lw=1.2, zorder=1)
    ax.errorbar(across_ci[0], yagg, xerr=[[across_ci[0]-across_ci[1]], [across_ci[2]-across_ci[0]]],
                fmt="o", color=C_ACROSS, ms=6, capsize=3, zorder=4)
    ax.errorbar(within_ci[0], yagg, xerr=[[within_ci[0]-within_ci[1]], [within_ci[2]-within_ci[0]]],
                fmt="o", color=C_WITHIN, ms=6, capsize=3, zorder=4)
    ax.text(-0.02, yagg, "AGGREGATE", fontsize=7.5, fontweight="bold", ha="right", va="center")
    ax.axhline(n + 0.3, color="#cccccc", lw=0.6, ls="--")

    ax.set_xlim(-0.02, 1.14)
    ax.text(1.11, n + 2.1, "gap", fontsize=6.5, ha="right", color="#333333", fontweight="bold")
    ax.set_xlabel("Advertisement-set similarity (Jaccard)", fontsize=9)
    ax.set_title("RQ3: Do delivered ads depend on the query?\n"
                 "within-query (same query) vs across-query (different queries)", fontsize=9.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8)
    leg = [Line2D([0], [0], marker="o", color="w", markerfacecolor=C_WITHIN, markersize=7, label="within-query (same query)"),
           Line2D([0], [0], marker="o", color="w", markerfacecolor=C_ACROSS, markersize=7, label="across-query (different queries)")]
    ax.legend(handles=leg, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=2, frameon=False)
    fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.2 + 0.4 / max(n, 4))
    for ext in ("pdf", "png"):
        fig.savefig(FIGDIR / f"fig_query_targeting{tag}.{ext}", dpi=200, bbox_inches="tight", facecolor="white")
    print(f"figure -> {FIGDIR / ('fig_query_targeting'+tag+'.pdf')} (+ .png)")


if __name__ == "__main__":
    main()
