# padel.how

- **Endpoint:** https://padel.how/mcp
- **Server:** padel.how Racket Catalogue 1.2.0
- **Ad-serving tool(s):** get_offers;search_rackets
- **Tool category:** shopping
- **Distinct ads observed:** 4 | **ad impressions:** 37
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** Read-only published racket catalogue. It does not provide recommendations; offer prices are published figures, not live prices.

## Evidence (why coded as advertising)
- *tool `get_offers`* — Amazon tag + per-offer affiliate disclosure || amzn.to link with per-offer 'Affiliate link. padel.how may earn a commission' || as 3918c66e1cb4
- *tool `search_rackets`* — as 3918c66e1cb4

## Example advertised items / links
- `amzn.to/4frOric`  (impressions: 10)
- `amzn.to/3RjVe4l`  (impressions: 9)
- `amzn.to/45yVCz3`  (impressions: 9)
- `www.amazon.com/dp/B0FZX2P72Q?tag=padelhow-20`  (impressions: 9)

## All tools exposed by this server
### `search_rackets`
Search published rackets using literal, case-insensitive catalogue filters.

### `get_racket`
Get one published racket by its validated catalogue slug.

### `compare_rackets`
Compare two to four distinct published racket slugs.

### `list_racket_brands`
List brand variants grouped by case-insensitive normalized spelling.

### `get_offers`
List published retailer offers per racket; prices carry observed_at and are not live.
