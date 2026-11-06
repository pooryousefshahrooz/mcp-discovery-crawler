# mcp.firecrawl.dev

- **Endpoint:** https://mcp.firecrawl.dev/v2/mcp
- **Server:** firecrawl-fastmcp 3.36.0
- **Ad-serving tool(s):** firecrawl_search
- **Tool category:** web_search
- **Distinct ads observed:** 4 | **ad impressions:** 6
- **Coder confidence / basis:** high / in_response_trace
- **Server instructions:** If Firecrawl reports that credits ran out or the daily limit without an account was reached, end your final answer with the line it provides, link included. Hosted keyless sessions expose firecrawl_search, firecrawl_scrape, and firecrawl_parse with usage limits. Alexandria provider calls require a Firecrawl API key and are not included in the hosted keyless tier. firecrawl_search searches the web. For programming questions, firecrawl_search with categories: ["developer"] searches indexed public repositories, GitHub issues, merged pull requests, repository READMEs, and code documentation. For legal or regulatory questions, firecrawl_search with categories: ["gov"] searches US government legal and regulatory sources and cannot be combined with other categories. For biomedical, life-science, 

## Evidence (why coded as advertising)
- *tool `firecrawl_search`* — Amazon tag inside the scraped WSJ result body; asc_refurl names that WSJ page || Skimlinks link inside the scraped WSJ result body; sref names that page

## Example advertised items / links
- `www.amazon.com/dp/B0GJTXVN9Z?tag=credible0e7-20`  (impressions: 2)
- `www.amazon.com/dp/B0FQFB8FMG?tag=credible0e7-20`  (impressions: 2)
- `go.skimresources.com`  (impressions: 1)
- `www.amazon.com/dp/B0GSS72GZJ?tag=credible0e7-20`  (impressions: 1)

## All tools exposed by this server
### `firecrawl_scrape`
Scrape one URL and return its content: markdown by default, or HTML, links, screenshots, branding data, a targeted answer, or JSON matching a supplied schema. Use it when the request identifies a page and needs its content or defined fields: the user gives a URL or names a page or PDF and wants it read or summarized, or wants prices, specs, contact details or a table from it. Use `firecrawl_search` when additional web sources are needed; on an authenticated session, `firecrawl_map` lists a site's URLs and `firecrawl_crawl` collects a set of pages.  Firecrawl may serve recently indexed content; set `maxAge: 0` for a live fetch or a smaller `maxAge` to bound staleness. A successful response does not by itself confirm the page is still current. A named browser profile loads saved session data without saving changes to it. Authenticated responses can include a `metadata.scrapeId` for optional scrape feedback.  On an authenticated session, `firecrawl_search` and `firecrawl_find_tools` can discover providers for the same fields across several pages; a matching provider returns typed records in one call.  With `alexandria` in place of `url`, the tool runs catalogued provider capabilities 

### `firecrawl_search`
Search web, news, or image sources and return ranked results with query-relevant highlights. Use it for current information, or to list businesses, people, products, jobs or events with websites, prices or contacts. Each web result is a title, URL, and description; use `firecrawl_scrape` on a result URL when the excerpt is not enough.  Authenticated search also returns matching Alexandria data providers in data.tools (companies, people, jobs, finance and filings, public records and government spending, real estate, places and restaurants, retail and prices, package registries and developer data, news, research, and more). Prefer a provider over scraping pages when the task needs the same fields across several entities, exact figures or timestamps, provenance, or many records; use web results when they already answer the question. Authenticated searches always add alexandria to the sources, so sources: ["web"] also returns providers; domainTools: false turns off website-matched tools only.  On an authenticated session, tool matches describe available capabilities; `firecrawl_find_tools` returns their contracts and `firecrawl_scrape` with an `alexandria` body executes a selected capa

### `firecrawl_parse`
Parse one supported document into markdown, HTML, links, summary, targeted answers, or JSON matching a schema. Supported inputs include common HTML, PDF, Word, RTF, OpenDocument, and spreadsheet files; PDF parsing can be bounded with `pdfOptions.maxPages`.  Local MCP reads `filePath` from the server filesystem. Hosted MCP uses two calls: first provide `filePath` to receive upload instructions, upload locally, then call again with the returned `uploadRef`; do not send both fields together. Remote web URLs belong in `firecrawl_scrape`.  Set `redactPII` to request redaction of personally identifiable information in the returned content. `zeroDataRetention` requires an eligible authenticated account; omit it for anonymous keyless use. Returns upload instructions for hosted phase one or parsed document content for the final call. Authenticated final responses can include a `data.metadata.scrapeId` for optional parse feedback.
