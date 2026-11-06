#!/usr/bin/env python3
"""Build the MCP server dataset release:
  1. all_mcp_servers.csv       -- every MCP server we connected to and enumerated tools from
  2. ad_servers/               -- the servers that served advertisements, with tools + ad evidence
     - ad_servers_summary.csv
     - ad_servers/<host>.md    -- per server: endpoint, server info, full tool list, ad evidence

Sources (read-only):
  fresh_measurement/runs/2026-10-29-full/endpoints/*.json   enumerated servers (tools+schemas)
  directories/endpoints.csv                                  which directories listed each endpoint
  analysis/ad_provenance/out/ad_provenance_results.csv       51 confirmed ad servers (coded)
  analysis/ad_provenance/out/ad_items.csv                    example ad items + URLs per server
"""
import csv, json, glob, collections, sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
ADDIR = OUT / "ad_servers"
ADDIR.mkdir(parents=True, exist_ok=True)
EPDIR = ROOT / "fresh_measurement/runs/2026-10-29-full/endpoints"
csv.field_size_limit(10_000_000)


def host_of(url):
    return (urlsplit(url).hostname or url or "").lower()


def load_dir_meta():
    m = {}
    p = ROOT / "directories/endpoints.csv"
    if p.exists():
        for r in csv.DictReader(open(p)):
            m[r["endpoint"].rstrip("/")] = r
    return m


def build_all_servers(dirmeta):
    rows = []
    files = sorted(glob.glob(str(EPDIR / "*.json")))
    for f in files:
        try:
            d = json.load(open(f))
        except Exception:
            continue
        ep = (d.get("endpoint") or "").strip()
        si = d.get("server_info") or {}
        tools = d.get("tools") or []
        dm = dirmeta.get(ep.rstrip("/"), {})
        rows.append({
            "host": host_of(ep),
            "endpoint": ep,
            "status": d.get("status", ""),
            "server_name": si.get("name", ""),
            "server_version": si.get("version", ""),
            "n_tools": len(tools),
            "n_prompts": len(d.get("prompts") or []),
            "has_instructions": int(bool(d.get("instructions"))),
            "listed_in_directories": dm.get("n_sources", ""),
            "directory_sources": dm.get("sources", ""),
            "auth_stated": dm.get("auth_stated", ""),
            "transports": dm.get("transports", ""),
        })
    # de-dup by endpoint, keep the record with most tools
    best = {}
    for r in rows:
        k = r["endpoint"]
        if k not in best or r["n_tools"] > best[k]["n_tools"]:
            best[k] = r
    rows = sorted(best.values(), key=lambda r: (-r["n_tools"], r["host"]))
    cols = ["host", "endpoint", "status", "server_name", "server_version", "n_tools",
            "n_prompts", "has_instructions", "listed_in_directories", "directory_sources",
            "auth_stated", "transports"]
    with open(OUT / "all_mcp_servers.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    enum = sum(1 for r in rows if r["n_tools"] > 0)
    print(f"all_mcp_servers.csv: {len(rows)} endpoints ({enum} with >=1 tool)")
    return rows


def index_endpoint_files():
    """host -> endpoint file with the most tools (for pulling ad servers' tool lists)."""
    idx = {}
    for f in glob.glob(str(EPDIR / "*.json")):
        base = Path(f).name
        host = base.rsplit("__", 1)[0]
        try:
            d = json.load(open(f))
        except Exception:
            continue
        nt = len(d.get("tools") or [])
        if host not in idx or nt > idx[host][1]:
            idx[host] = (f, nt, d)
    return idx


def build_ad_servers(epidx):
    results = list(csv.DictReader(open(ROOT / "analysis/ad_provenance/out/ad_provenance_results.csv")))
    items = list(csv.DictReader(open(ROOT / "analysis/ad_provenance/out/ad_items.csv")))
    items_by_server = collections.defaultdict(list)
    for it in items:
        items_by_server[it["server"]].append(it)

    # aggregate results per server (a server may have multiple tool rows)
    by_server = collections.defaultdict(list)
    for r in results:
        by_server[r["server"]].append(r)

    summ = []
    for host in sorted(by_server):
        recs = by_server[host]
        d = epidx.get(host)
        epfile = d[2] if d else {}
        tools = epfile.get("tools") or []
        ep = epfile.get("endpoint", "")
        si = epfile.get("server_info") or {}
        n_ads = sum(int(x["distinct_ads"]) for x in recs)
        n_imp = sum(int(x["impressions"]) for x in recs)
        cats = ";".join(sorted({x["tool_category"] for x in recs}))
        conf = ";".join(sorted({x["confidence"] for x in recs}))
        basis = ";".join(sorted({x["basis"] for x in recs}))
        ad_tools = ";".join(sorted({x["tool"] for x in recs}))
        exs = items_by_server.get(host, [])
        example = exs[0]["example"] if exs else ""
        summ.append({
            "host": host, "endpoint": ep, "server_name": si.get("name", ""),
            "ad_tools": ad_tools, "tool_category": cats,
            "n_distinct_ads": n_ads, "n_impressions": n_imp,
            "confidence": conf, "basis": basis, "n_tools_total": len(tools),
            "example_ad_url": example,
        })

        # per-server markdown
        md = [f"# {host}", ""]
        md.append(f"- **Endpoint:** {ep or '(endpoint file not found)'}")
        md.append(f"- **Server:** {si.get('name','?')} {si.get('version','')}".rstrip())
        md.append(f"- **Ad-serving tool(s):** {ad_tools}")
        md.append(f"- **Tool category:** {cats}")
        md.append(f"- **Distinct ads observed:** {n_ads} | **ad impressions:** {n_imp}")
        md.append(f"- **Coder confidence / basis:** {conf} / {basis}")
        if epfile.get("instructions"):
            md.append(f"- **Server instructions:** {str(epfile['instructions'])[:800]}")
        md.append("")
        md.append("## Evidence (why coded as advertising)")
        for r in recs:
            ev = (r.get("evidence") or "").strip()
            md.append(f"- *tool `{r['tool']}`* — {ev[:600]}" if ev else f"- tool `{r['tool']}`")
        md.append("")
        md.append("## Example advertised items / links")
        for it in exs[:15]:
            md.append(f"- `{it['identity']}`  (impressions: {it['impressions']})")
        if len(exs) > 15:
            md.append(f"- … and {len(exs)-15} more (see analysis/ad_provenance/out/ad_items.csv)")
        md.append("")
        md.append("## All tools exposed by this server")
        if tools:
            for t in tools:
                name = t.get("name", "?")
                desc = (t.get("description") or "").replace("\n", " ").strip()
                md.append(f"### `{name}`")
                md.append(desc[:1200] if desc else "_(no description)_")
                md.append("")
        else:
            md.append("_(tool list not available in the enumerated snapshot)_")
        (ADDIR / f"{host}.md").write_text("\n".join(md), encoding="utf-8")

    cols = ["host", "endpoint", "server_name", "ad_tools", "tool_category",
            "n_distinct_ads", "n_impressions", "confidence", "basis",
            "n_tools_total", "example_ad_url"]
    with open(ADDIR / "ad_servers_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(summ)
    print(f"ad_servers_summary.csv: {len(summ)} ad servers; wrote {len(summ)} per-server .md files")
    return summ


def main():
    dirmeta = load_dir_meta()
    allrows = build_all_servers(dirmeta)
    epidx = index_endpoint_files()
    summ = build_ad_servers(epidx)
    return allrows, summ


if __name__ == "__main__":
    main()
