# Codebook: advertisement status and origin in MCP tool responses

Unit of coding: one **signature** (SIG) from `out/review_sheet.md`. A signature is one link or label
mechanism of one (server, tool). Code each SIG once from the evidence on the sheet: the
example response excerpts, the tool description, and the server instructions. You may open the raw
response files under `ad_probe/results/` for more context.

Do **not** follow, fetch, or click any link in the responses. Every link may carry an affiliate
tag, and opening it would register a click.

## Field 1: `status` (pick one)

| code | definition |
|---|---|
| `confirmed_ad` | The returned item is (a) marked as sponsored/promoted/an ad by the response, (b) or carries a link whose paid or affiliate nature is verifiable from the link itself (a known affiliate-network host; an affiliate program's tracking parameter such as Amazon `tag=xxx-20`, Awin, Impact, CJ, eBay EPN `campid`), (c) or carries a link or redirect whose affiliate or referral nature is stated in the response, the tool description or the server instructions. |
| `promotional` | Promotes the operator's own site, product or service, or tags the operator's own links for attribution (UTM, `src=`). There is no evidence of a paid or affiliate relationship. |
| `commercial_other` | Advertising-industry material that is not an ad impression for the end user: ad-inventory listings, ad-tech API docs, or an affiliate link sitting inside a third party's example payload or description. |
| `not_ad` | The pattern matched but there is no ad: an empty placement, disclosure boilerplate with no item, a negative flag, a generic link (docs, GitHub, images), or click tracking to a destination with no affiliate or paid evidence. |

Not every commercial search result is a paid placement. An organic product, job or listing
result is **not** an ad unless it meets (a), (b) or (c).

## Field 2: `origin` (for `confirmed_ad`, `promotional` and `commercial_other`)

Where did the ad element (the label, link or tracking parameter) enter the response? Apply the
rules **in order** and take the first that fits:

1. `third_party_content`: the element sits inside content the response attributes to a retrieved
   third-party page or listing. Examples: inside a scraped page body or markdown of result URL X;
   a referrer parameter naming page X; a field such as `source`, `provider` or `booking.source`
   naming a third-party *website* the record was taken from. The server must not describe itself
   as adding such links.
2. `upstream_api`: a provenance field or the documentation names an upstream search or data
   **API/feed** as the supplier of the element itself, not merely of the surrounding organic data.
3. `operator`: the element is produced by the MCP server operator. Evidence includes a redirect
   or tracking endpoint on the server's own host; a sponsored or promoted flag or rank emitted by
   the server's own ranking; tool or server docs stating that the server adds affiliate, referral
   or sponsored links; or source code. Upstream organic data wrapped by the operator's affiliate
   link counts as `operator`, because the ad element is the wrapper.
4. `multiple`: the evidence shows two of the above contributed the **same** ad element. For
   example, an upstream feed supplied an affiliate link and the operator wrapped it again.
5. `unknown`: none of the above is established.

**Prohibited inferences:**
- Never assign origin from the server's domain name, a promotional keyword, or the text of an
  affiliate tag alone. For example, `tag=voyagehacks-20` is not evidence that VoyageHacks added
  it.
- Never assign `operator` because an ad is absent from some other, non-identical upstream request.
- Origin means where the content came from. It says nothing about who earns the revenue; do not
  code revenue.

## Field 3: `basis`: the strongest evidence used (pick one)

`source_code` > `in_response_trace` (provenance field, referrer parameter, position inside a
scraped page, a server-emitted sponsored flag or rank) > `documentation` (tool description or
server instructions) > `own_host_redirect_only` > `none`.

## Field 4: `confidence`

- `high`: `source_code`, or an unambiguous `in_response_trace`.
- `medium`: `documentation` that self-describes the mechanism, consistent with the response.
- `low`: `own_host_redirect_only`, a single unverified provenance field, or indirect evidence.

## Field 5: `tool_category` (of the tool, from its description)

`web_search` (general web search or search-and-scrape), `browsing_scraping` (fetch/scrape a given
URL), `shopping` (product catalog, deals, price comparison, coupons), `ad_network` (a tool whose
purpose is serving or selling ads), `other` (jobs, events, travel, finance, B2B, legal, ...).

## Output format

A JSON object keyed by SIG id:

```json
{"<sig>": {"status": "...", "origin": "...", "basis": "...", "confidence": "...",
           "tool_category": "...", "note": "one sentence: the decisive evidence"}}
```

For attribution-only signatures, list only those you code as something other than `promotional`.
