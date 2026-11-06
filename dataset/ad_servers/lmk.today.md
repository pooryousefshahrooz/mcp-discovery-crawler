# lmk.today

- **Endpoint:** https://lmk.today/api/ucp/mcp
- **Server:** lmk-today 1.0.0
- **Ad-serving tool(s):** get_gift_ideas;search;search_catalog
- **Tool category:** shopping
- **Distinct ads observed:** 156 | **ad impressions:** 762
- **Coder confidence / basis:** high / in_response_trace
- **Server instructions:** LMK.today returns shoppable products from a curated cross-merchant catalog.

When presenting any product to the user:
- ALWAYS link it. Render the product name as a markdown link to its `url` field (an LMK product page). Never list a product without its link.
- Preserve the full `url`, including its query string — it carries click attribution. Do not shorten it, strip parameters, or substitute a merchant URL.
- When `originalPrice` and `discountPercent` are present, show the savings, e.g. "**$25.71** ~~$55~~ (−53%)". For deal/discount queries, lead with the discount percentage.
- Prices are in each product's `currency`. `rating`, `reviewCount`, and `wishlistCount` are aggregate signals you may cite.

Links resolve to LMK product pages (not merchants); LMK may earn an affiliate commission a

## Evidence (why coded as advertising)
- *tool `get_gift_ideas`* — Both coders: confirmed/operator. Confidence lowered on B's caveat: the server field is named aff_url and points to a /bid/redirect on r.v2i8b.com, which is not a known affiliate network, and lmk.today publishes no affiliate disclosure; the Amazon-tag links of the same wrapper are verifiable and stay high/medium. || Own-host lmk.today/c/ click redirect wrapping an Amazon link with tag=lmk.today-20 (Associates tag); the operator's wrapper carries the affiliate destination. || Own-host lmk.today/c/ redirect to Wayfair carrying an aff_url parameter pointing to a bid/redirect host with campaign_id/
- *tool `search`* — Own-host lmk.today/c/ redirect to Wayfair with an aff_url bid-redirect parameter (campaign_id/sub_id); affiliate nature only weakly verifiable. || Own-host lmk.today/c/ redirect wrapping an Amazon tag=lmk.today-20 affiliate link (mixed with Wayfair links that carry an aff_url bid redirect). || affiliate link (Amazon tag=lmk.today-20 / aff_url bid-redirect) nested in the operator's /c/ click wrapper; instructions: query string carries click attribution || as e8862bf4169e
- *tool `search_catalog`* — Own-host lmk.today/c/ redirect to Wayfair with an aff_url bid-redirect parameter; affiliate nature only weakly verifiable. || Own-host lmk.today/c/ redirect wrapping an Amazon tag=lmk.today-20 affiliate link. || affiliate link (Amazon tag=lmk.today-20 / aff_url bid-redirect) nested in the operator's /c/ click wrapper; instructions: query string carries click attribution || as e8862bf4169e

## Example advertised items / links
- `www.amazon.com/dp/B098K19W5G?tag=lmk.today-20`  (impressions: 18)
- `www.amazon.com/dp/B000ARG5S4?tag=lmk.today-20`  (impressions: 18)
- `www.amazon.com/dp/B087TPWKFJ?tag=lmk.today-20`  (impressions: 18)
- `www.amazon.com/dp/B0C2JK9Y8V?tag=lmk.today-20`  (impressions: 18)
- `www.wayfair.com/Melitta--Melitta-Aroma-Tocco-10cup-Drip-Coffee-Maker-With-Glass-Carafe-And-Touch-Control-Display-MCM009PULBK0-L896-K~NDDR1029.html`  (impressions: 18)
- `www.amazon.com/dp/B0DJRSJ3N3?tag=lmk.today-20`  (impressions: 18)
- `www.walmart.com/ip/Automated-Market-Makers-A-Practical-Guide-to-Decentralized-Exchanges-and-Cryptocurrency-Trading-Paperback-9781484286159/1696943709`  (impressions: 18)
- `www.amazon.com/dp/B09786LXCB?tag=lmk.today-20`  (impressions: 18)
- `www.amazon.com/dp/B09TR3KJ54?tag=lmk.today-20`  (impressions: 18)
- `www.amazon.com/dp/B0DJFJWK21?tag=lmk.today-20`  (impressions: 18)
- `www.amazon.com/dp/B06XQWDNXD?tag=lmk.today-20`  (impressions: 18)
- `www.amazon.com/dp/1334583269?tag=lmk.today-20`  (impressions: 18)
- `www.walmart.com/ip/Your-Retirement-Portfolio-Tax-Free-Income-for-Life-9781483994093/500615277`  (impressions: 18)
- `www.walmart.com/ip/Baby-Ddrops-Liquid-Organic-Vitamin-D3-Supplement-Drops-400-IU-per-Drop-0-06-fl-oz/19368604224`  (impressions: 18)
- `www.wayfair.com/Yamazaki-Home--Yamazaki-Home-Vitamin-and-Supplement-Organizer-Tray-with-Handle-11036-L7341-K~YZUS2136.html?PiID%5B%5D=135545106`  (impressions: 18)
- … and 38 more (see analysis/ad_provenance/out/ad_items.csv)

## All tools exposed by this server
### `search`
Search LMK products; returns citable results, each with a canonical LMK product-page URL. Use for shopping/discovery. For price/brand/on-sale filters, use search_catalog.

### `fetch`
Fetch full detail for one product by id (from a prior search result). Returns citable text with price, savings, 90-day price history, and buying options.

### `search_catalog`
Search LMK's curated cross-merchant catalog. Returns products with LMK product-page links. Use for "find me X" shopping queries.

### `lookup_catalog`
Batch-resolve products by LMK slug, id, or external/merchant id.

### `get_product`
Get a single product with full detail: enriched card, 90-day price stats (lowest/highest/average + is-at-lowest), and cross-merchant buying options.

### `compare_prices`
Compare a product's price across merchants. Returns offers plus lowest/highest, all linking to the LMK product page.

### `get_price_history`
Get price history and stats for a product over a trailing window (default 90 days). LMK-proprietary price intelligence.

### `get_deals`
Today's best deals, ranked by LMK's deal-quality scoring (discount depth, price sweet spot, merchant quality). Optionally filter by category slug or minimum discount.

### `get_popular_products`
Most-wishlisted products (180-day demand signal across all LMK lists, aggregate counts only). Unique LMK demand data.

### `get_trending_products`
Products gaining momentum — most-added to wishlists in the last 30 days (aggregate counts only).

### `get_gift_ideas`
Gift recommendations for a recipient/occasion within a budget. Blends curated search with LMK demand signals.

### `list_collections`
List LMK's published editorial collections (occasions, holidays, beauty, style, sports).

### `get_collection`
Get a single editorial collection and its curated products by slug.
