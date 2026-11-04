#!/usr/bin/env python3
"""M4 - Figures for the ad-metadata study (reads M3's CSVs only).

  fig_ad_metadata_heatmap.{pdf,png}      top-30 servers x 8 categories, exposure rate (% of ad responses)
  fig_ad_metadata_heatmap_full.{pdf,png} every server with >=1 ad-containing response
  fig_ad_metadata_prevalence.{pdf,png}   % of servers exposing each category (n eligible per bar)

Cell value = rate_any (explicit + inferred); cells supported only by inferred evidence carry a
superscript 'i'. N/A (demonstrably inapplicable, coding/applicability.json) is hatched grey.
Colour: single-hue blue sequential ramp, white = 0%.

  python3 analysis/ad_metadata/m4_figures.py
"""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FIG = HERE / "figs"
CATS = ["disclosure", "advertiser", "campaign", "bid", "score", "competing", "winner", "tracking"]
COLS = ["Disclosure", "Advertiser", "Campaign\nID", "Bid", "Auction/\nrank score", "No.\ncompeting",
        "Winner\nID", "Affiliate/\ntracking ID"]
RAMP = ["#ffffff", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
CMAP = LinearSegmentedColormap.from_list("blue_seq", RAMP)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.linewidth": 0.6,
                     "pdf.fonttype": 42, "ps.fonttype": 42})

SHORT = {"dealsping-ai.akhilbabumfwa.workers.dev": "dealsping-ai (workers.dev)",
         "mcp-production-680d.up.railway.app": "golf-deals (railway.app)",
         "mcp-server-nani-v3-20.up.railway.app": "aloha mirror (railway.app)",
         "mcp.supplementenscanner.nl": "supplementenscanner.nl",
         "socialbridge-mcp.vercel.app": "socialbridge (vercel.app)",
         "bluesky.caseyjhand.com": "bluesky.caseyjhand.com"}


def label(h):
    return SHORT.get(h, h.removeprefix("mcp.").removeprefix("www."))


def load():
    cells = defaultdict(dict)
    for r in csv.DictReader(open(OUT / "exposure_by_server_category.csv")):
        cells[r["server"]][r["category"]] = r
    srv = {r["server"]: r for r in csv.DictReader(open(OUT / "server_summary.csv"))}
    hosts = [h for h in srv if int(srv[h]["ad_containing"]) > 0]

    def key(h):
        rates = sum(float(cells[h][c]["rate_any_pct"] or 0) for c in CATS)
        return (-int(srv[h]["n_cats_any"]), -int(srv[h]["n_cats_explicit"]), -rates, h)
    return cells, srv, sorted(hosts, key=key)


def heatmap(cells, srv, hosts, path, title_n):
    n = len(hosts)
    fig_h = 0.62 + 0.142 * n
    fig, ax = plt.subplots(figsize=(3.4, fig_h))
    for i, h in enumerate(hosts):
        for j, c in enumerate(CATS):
            x = cells[h][c]
            if x["status"] == "not_applicable":
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor="#f0efec", edgecolor="#b8b7b2",
                                       hatch="/////", linewidth=0))
                ax.text(j + .5, i + .5, "N/A", ha="center", va="center", fontsize=5.2, color=INK2)
                continue
            v = float(x["rate_any_pct"] or 0)
            ax.add_patch(Rectangle((j, i), 1, 1, facecolor=CMAP(v / 100), linewidth=0))
            if v > 0:
                s = f"{v:.0f}" + ("ᶦ" if x["status"] == "inferred_only" else "")
                ax.text(j + .5, i + .5, s, ha="center", va="center", fontsize=5.6,
                        color="white" if v >= 55 else INK)
            else:
                ax.text(j + .5, i + .5, "·", ha="center", va="center", fontsize=6, color="#a9a8a3")
    for k in range(n + 1):
        ax.axhline(k, color="white", lw=0.8)
    for k in range(len(CATS) + 1):
        ax.axvline(k, color="white", lw=0.8)
    ax.set_xlim(0, len(CATS))
    ax.set_ylim(n, 0)
    ax.set_yticks([i + .5 for i in range(n)])
    ax.set_yticklabels([f"{label(h)}  (n={srv[h]['ad_containing']})" for h in hosts], fontsize=6)
    ax.set_xticks([j + .5 for j in range(len(CATS))])
    ax.set_xticklabels([c.replace("\n", " ") for c in COLS], fontsize=5.8, rotation=40, ha="left",
                       rotation_mode="anchor")
    ax.xaxis.tick_top()
    ax.tick_params(length=0, pad=2)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.axvline(3, color=INK2, lw=0.5, ls=(0, (2, 2)))
    ax.axvline(7, color=INK2, lw=0.5, ls=(0, (2, 2)))
    sm = plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, 100))
    cb = fig.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.025 * 30 / max(n, 30), pad=0.012,
                      aspect=40)
    cb.set_label("Exposure rate (% of the server's ad-containing responses)\n"
                 "ᶦ inferred only · N/A demonstrably not applicable · n = ad-containing responses",
                 fontsize=5.4, color=INK2)
    cb.ax.tick_params(labelsize=5.5, length=2)
    cb.outline.set_linewidth(0.4)
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    fig.savefig(path.with_suffix(".png"), dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def prevalence():
    rows = list(csv.DictReader(open(OUT / "category_prevalence.csv")))
    labels = {"disclosure": "Ad disclosure", "advertiser": "Advertiser identity", "campaign": "Campaign ID",
              "bid": "Bid amount", "score": "Auction/ranking score", "competing": "No. competing campaigns",
              "winner": "Winning campaign ID", "tracking": "Affiliate/tracking ID"}
    rows = list(reversed(rows))
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    y = range(len(rows))
    pe = [float(r["pct_explicit"]) for r in rows]
    pa = [float(r["pct_any"]) for r in rows]
    ax.barh(y, pa, height=0.62, color="#cde2fb", edgecolor="#6da7ec", linewidth=0.5, hatch="////",
            label="incl. inferred")
    ax.barh(y, pe, height=0.62, color="#2a78d6", linewidth=0, label="explicitly reported")
    for i, r in enumerate(rows):
        a, e, n = int(r["servers_any"]), int(r["servers_explicit"]), int(r["eligible_servers"])
        txt = f"{e}/{n}" + (f"  (+{a - e} inferred)" if a > e else "")
        ax.text(max(pa[i], pe[i]) + 1.5, i, txt, va="center", fontsize=6, color=INK)
    ax.set_yticks(list(y))
    ax.set_yticklabels([labels[r["category"]] for r in rows], fontsize=6.5)
    ax.set_xlim(0, 112)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("% of eligible servers exposing the category at least once", fontsize=6.5, color=INK2)
    ax.tick_params(labelsize=6, length=2, colors=INK2)
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=5.8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    nall = max(int(r["eligible_servers"]) + int(r["na_servers"]) for r in rows)
    nna = max(int(r["na_servers"]) for r in rows)
    ax.set_title(f"n = {nall} servers with ad-containing responses (auction fields: {nall - nna}; "
                 f"{nna} N/A)", fontsize=6, color=INK2, loc="left")
    fig.savefig(FIG / "fig_ad_metadata_prevalence.pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(FIG / "fig_ad_metadata_prevalence.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    cells, srv, hosts = load()
    heatmap(cells, srv, hosts[:30], FIG / "fig_ad_metadata_heatmap", 30)
    heatmap(cells, srv, hosts, FIG / "fig_ad_metadata_heatmap_full", len(hosts))
    prevalence()
    print(f"heatmap rows: main {min(30, len(hosts))}, full {len(hosts)} -> {FIG}")


if __name__ == "__main__":
    main()
