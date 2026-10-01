#!/usr/bin/env python3
"""Enumerate remote MCP endpoints from public MCP directories.

Usage:  python3 directories/collect.py --source {official,smithery,glama,mcpso,mcpdirectory} [--limit N]

Per source, the most structured mechanism available (checked 2026-09-30):
  official      registry.modelcontextprotocol.io  public JSON API (/v0/servers, cursor paging)
  smithery      registry.smithery.ai              public JSON API (list + per-server detail)
  glama         glama.ai                          API needs a key -> public sitemap
                                                  (mcp-remote-servers/*.xml) + listing pages
  mcpso         mcp.so                            no public API (/api/ disallowed) -> sitemap + pages
  mcpdirectory  mcp.directory                     no public API (/api/ disallowed) -> sitemap + pages
  (PulseMCP: API v0.1 needs an X-API-Key; website is behind a Cloudflare challenge -> not collected)

One JSON line per listing endpoint is appended to directories/raw/<source>.jsonl
as soon as it is parsed (resumable: listings already written are skipped).
Fields: source, server_name, listing_url, endpoint, transport, auth, extra
"""
import argparse
import asyncio
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

import httpx

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
UA = "mcp-discovery-measurement/1.0 (academic research; directory enumeration)"
CONC = {"official": 1, "smithery": 4, "glama": 3, "mcpso": 3, "mcpdirectory": 3}
DELAY = 0.25          # seconds between requests per worker


class Sink:
    """Append-only writer with resume support keyed on listing_url."""

    def __init__(self, source):
        RAW.mkdir(exist_ok=True)
        self.path = RAW / f"{source}.jsonl"
        self.done = set()
        if self.path.exists():
            for line in open(self.path):
                try:
                    self.done.add(json.loads(line)["listing_url"])
                except (ValueError, KeyError):
                    pass
        self.f = open(self.path, "a")

    def write(self, recs):
        for r in recs:
            self.f.write(json.dumps(r, ensure_ascii=False) + "\n")
        self.f.flush()


def rec(source, name, listing, endpoint, transport="", auth="", **extra):
    return {"source": source, "server_name": name, "listing_url": listing, "endpoint": endpoint or "",
            "transport": transport or "", "auth": auth or "", "extra": extra}


async def get(client, url, **kw):
    for attempt in range(4):
        try:
            r = await client.get(url, timeout=40, **kw)
            if r.status_code in (429, 502, 503):
                await asyncio.sleep(5 * (attempt + 1))
                continue
            return r
        except httpx.HTTPError:
            await asyncio.sleep(3 * (attempt + 1))
    return None


def sitemap_locs(xml):
    return [html.unescape(u) for u in re.findall(r"<loc>([^<]+)</loc>", xml)]


# ---------------------------------------------------------------- official
async def official(client, sink, limit):
    cursor, n = None, 0
    while True:
        url = "https://registry.modelcontextprotocol.io/v0/servers?limit=100" + (f"&cursor={quote(cursor)}" if cursor else "")
        r = await get(client, url)
        if r is None or r.status_code != 200:
            print("official: stopped at", url, r and r.status_code); return
        d = r.json()
        out = []
        for item in d.get("servers", []):
            s, meta = item.get("server", {}), (item.get("_meta") or {}).get("io.modelcontextprotocol.registry/official", {})
            if not meta.get("isLatest", True):
                continue
            listing = f"https://registry.modelcontextprotocol.io/v0/servers/{quote(s.get('name', ''), safe='')}"
            for i, rm in enumerate(s.get("remotes") or []):
                hdrs = rm.get("headers") or []
                auth = ", ".join(f"header {h.get('name')}{' (required)' if h.get('isRequired') else ''}"
                                 for h in hdrs if isinstance(h, dict)) or "none stated"
                lk = listing + (f"#remote{i}" if i else "")
                if lk in sink.done:
                    continue
                out.append(rec("official", s.get("title") or s.get("name"), lk, rm.get("url"), rm.get("type"), auth,
                               registry_name=s.get("name"), version=s.get("version"), status=meta.get("status")))
        sink.write(out); n += len(out)
        cursor = (d.get("metadata") or {}).get("nextCursor")
        print(f"official: +{len(out)} (total {n})", flush=True)
        if not cursor or (limit and n >= limit):
            return


# ---------------------------------------------------------------- smithery
async def smithery(client, sink, limit):
    # The list API caps every query at 500 results, so enumerate from the public
    # server sitemap and fetch each server's (uncapped) detail record instead.
    locs = await sitemap_urls(client, "https://smithery.ai/sitemap_index.xml", lambda l: "/servers/sitemap/" in l)
    qns = {l.split("/servers/", 1)[1] for l in locs if "/servers/" in l and "/sitemap/" not in l}
    print(f"smithery: {len(qns)} servers in sitemap (its pages all repeat the same list)", flush=True)
    # Union with capped API searches: filters plus common topic words (each <= 500 results).
    queries = ["is:remote", "is:deployed", "is:verified"] + (
        "search web browser github git database sql postgres mysql mongo redis file filesystem slack discord email gmail "
        "calendar notion jira linear figma youtube twitter reddit weather map finance stock crypto bitcoin wallet payment "
        "stripe shopify ecommerce news pdf image video audio music ai llm openai agent memory rag vector docs document "
        "code python javascript kubernetes docker aws azure gcp cloud security scan api http scraper crawl seo analytics "
        "marketing sales crm hubspot salesforce travel flight hotel health medical legal education math science research "
        "paper arxiv translate language time weather sports game chess job hr recruit real estate property tax invoice "
        "accounting bank trade market data chart excel sheet google microsoft apple android ios linux shell terminal "
        "ssh test monitor log devops ci deploy weather chinese china japan korea india brazil").split()
    before = len(qns)
    for q in dict.fromkeys(queries):
        for page in range(1, 6):
            r = await get(client, f"https://registry.smithery.ai/servers?pageSize=100&page={page}&q={quote(q)}")
            await asyncio.sleep(DELAY)
            if r is None or r.status_code != 200:
                break
            d = r.json()
            qns |= {s["qualifiedName"] for s in d.get("servers", [])}
            if page >= d["pagination"]["totalPages"]:
                break
    print(f"smithery: +{len(qns) - before} from API searches -> {len(qns)} servers", flush=True)
    qns = sorted(qns)
    todo = [q for q in qns if f"https://smithery.ai/servers/{q}" not in sink.done]
    if limit:
        todo = todo[:limit]
    sem, done = asyncio.Semaphore(CONC["smithery"]), 0

    async def one(qn):
        nonlocal done
        async with sem:
            listing = f"https://smithery.ai/servers/{qn}"
            r = await get(client, f"https://registry.smithery.ai/servers/{quote(qn, safe='@/')}")
            await asyncio.sleep(DELAY)
            done += 1
            if done % 500 == 0:
                print(f"smithery: {done}/{len(todo)}", flush=True)
            if r is None or r.status_code != 200:
                sink.write([rec("smithery", "", listing, "", "", "", qualified_name=qn, error=r and r.status_code)]); return
            d = r.json()
            s = {"displayName": d.get("displayName")}
            if not d.get("remote"):
                sink.write([rec("smithery", d.get("displayName"), listing, "", "stdio", "", qualified_name=qn, remote=False)])
                return
            conns = d.get("connections") or []
            out = []
            for c in conns or [{}]:
                schema = (c.get("configSchema") or {})
                req = schema.get("required") or []
                auth = f"config required: {', '.join(req)}" if req else ("security: " + json.dumps(d.get("security"))[:80]
                                                                          if d.get("security") else "none stated")
                out.append(rec("smithery", d.get("displayName") or s.get("displayName"), listing,
                               c.get("deploymentUrl") or d.get("deploymentUrl"), c.get("type"), auth,
                               qualified_name=qn, remote=True, n_tools=len(d.get("tools") or [])))
            sink.write(out[:1] if len({o["endpoint"] for o in out}) == 1 else out)
    await asyncio.gather(*(one(q) for q in todo))


# ---------------------------------------------------------------- page-based sources
async def crawl_pages(client, sink, source, urls, parse, limit):
    urls = [u for u in urls if u not in sink.done]
    if limit:
        urls = urls[:limit]
    print(f"{source}: {len(urls)} pages to fetch", flush=True)
    sem, done = asyncio.Semaphore(CONC[source]), 0

    async def one(u):
        nonlocal done
        async with sem:
            r = await get(client, u)
            await asyncio.sleep(DELAY)
        if r is None or r.status_code != 200:
            sink.write([rec(source, "", u, "", error=r and r.status_code)])
        else:
            try:
                sink.write(parse(u, r.text) or [rec(source, "", u, "")])
            except Exception as e:  # keep going; record the parse failure
                sink.write([rec(source, "", u, "", parse_error=f"{type(e).__name__}: {e}")])
        done += 1
        if done % 200 == 0:
            print(f"{source}: {done}/{len(urls)}", flush=True)
    await asyncio.gather(*(one(u) for u in urls))


def parse_glama(u, t):
    name = re.search(r"<title>([^<|]+)", t)
    i = t.find(">Transport<")
    transport = url = ""
    if i >= 0:
        blk = t[i:i + 2500]
        m = re.search(r">\s*(Streamable HTTP|SSE|HTTP)\s*<", blk)
        transport = m.group(1) if m else ""
        m = re.search(r'<input[^>]*value="([^"]+)"', blk)
        url = html.unescape(m.group(1)) if m else ""
    auth = ""
    if url:
        j = t.find(json.dumps(url)[1:-1])
        seg = t[max(0, j - 4000): j + 4000] if j >= 0 else ""
        m = re.search(r'\\?"authType\\?",\\?"([a-z0-9_]+)', seg)
        auth = m.group(1) if m else ""
    return [rec("glama", html.unescape(name.group(1)).strip() if name else "", u, url, transport, auth)]


def parse_mcpso(u, t):
    i = t.find("isRemote:")
    if i < 0:
        return None
    seg = t[max(0, i - 3000): i + 3000]
    g = lambda k: (re.search(k + r':"((?:[^"\\]|\\.)*)"', seg) or [None, ""])[1]
    is_remote = seg[i - max(0, i - 3000) + 9: i - max(0, i - 3000) + 11] == "!0"
    transports = g("transports").replace('\\"', '"')
    cfg = g("config").encode().decode("unicode_escape", "ignore")
    urls = sorted(set(re.findall(r'"(?:url|serverUrl)"\s*:\s*"(https?://[^"]+)"', cfg)))
    name = g("name")
    if not urls:
        return [rec("mcpso", name, u, "", transports, g("authType"), is_remote=is_remote)]
    return [rec("mcpso", name, u + (f"#{k}" if k else ""), e, transports, g("authType") or "none stated",
                is_remote=is_remote) for k, e in enumerate(urls)]


def parse_mcpdirectory(u, t):
    d = t.replace('\\\\"', '"').replace('\\"', '"')
    tt = re.search(r'"transportType":\[([^\]]*)\]', d)
    transport = tt.group(1).replace('"', "") if tt else ""
    name = re.search(r"<title>([^<|–-]+)", t)
    urls = sorted(set(e.rstrip("\\") for e in re.findall(r'"url":\s*"(https?://[^"\\]+)', d)
                      if "mcp.directory" not in e and "github.com" not in e and not e.endswith((".png", ".svg"))))
    auth = "oauth mentioned" if re.search(r"OAuth", t) else ""
    if not urls:
        return [rec("mcpdirectory", name.group(1).strip() if name else "", u, "", transport, auth)]
    return [rec("mcpdirectory", name.group(1).strip() if name else "", u + (f"#{k}" if k else ""), e, transport, auth)
            for k, e in enumerate(urls)]


async def sitemap_urls(client, index_url, pick):
    r = await get(client, index_url)
    locs = sitemap_locs(r.text) if r is not None else []
    subs = [l for l in locs if pick(l)]
    if not subs:
        return locs
    out = []
    for s in subs:
        rr = await get(client, s)
        out += sitemap_locs(rr.text) if rr is not None else []
    return out


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=list(CONC))
    ap.add_argument("--limit", type=int, default=None, help="max listings (for testing)")
    a = ap.parse_args()
    sink = Sink(a.source)
    async with httpx.AsyncClient(headers={"User-Agent": UA}, follow_redirects=True) as client:
        if a.source == "official":
            await official(client, sink, a.limit)
        elif a.source == "smithery":
            await smithery(client, sink, a.limit)
        elif a.source == "glama":
            urls = await sitemap_urls(client, "https://glama.ai/sitemap.xml", lambda l: "mcp-remote-servers" in l)
            await crawl_pages(client, sink, "glama", [u for u in urls if "/mcp/connectors/" in u], parse_glama, a.limit)
        elif a.source == "mcpso":
            urls = await sitemap_urls(client, "https://mcp.so/sitemap.xml", lambda l: "section=servers" in l)
            await crawl_pages(client, sink, "mcpso", [u for u in urls if "/servers/" in u], parse_mcpso, a.limit)
        elif a.source == "mcpdirectory":
            urls = await sitemap_urls(client, "https://mcp.directory/sitemap.xml", lambda l: False)
            urls = [u for u in urls if re.match(r"https://mcp\.directory/servers/[^/]+$", u) and not u.endswith("/leaderboard")]
            await crawl_pages(client, sink, "mcpdirectory", urls, parse_mcpdirectory, a.limit)
    print("done:", a.source)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
