# cashbackpro.org

- **Endpoint:** https://cashbackpro.org/api/mcp
- **Server:** cashbackpro 0.3.0
- **Ad-serving tool(s):** get_promo_codes;search_products
- **Tool category:** shopping
- **Distinct ads observed:** 177 | **ad impressions:** 460
- **Coder confidence / basis:** medium / documentation

## Evidence (why coded as advertising)
- *tool `get_promo_codes`* — cashbackpro /api/go link; response note: already a CashbackPro affiliate link
- *tool `search_products`* — own-host /api/go product links; description: product URLs are CashbackPro affiliate links || same product links as a2a23d3de2d2, response disclosure covers them

## Example advertised items / links
- `cashbackpro.org/api/go/mcp/1005010675581764`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005009336647990`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005006972806997`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005007878387904`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005010325796385`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005013305311436`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005010325859220`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005012607893294`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005012314193352`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005007800790232`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005007740756045`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005009447232680`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005009880781283`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/32955350690`  (impressions: 6)
- `cashbackpro.org/api/go/mcp/1005007085721969`  (impressions: 6)
- … and 162 more (see analysis/ad_provenance/out/ad_items.csv)

## All tools exposed by this server
### `search_products`
Search the AliExpress catalogue and return compact product cards with price, rating, sales volume and the affiliate commission rate — the data needed to judge what a product actually costs. Low-quality listings are filtered out automatically (blocked categories, minimum price). Product URLs in the result are CashbackPro affiliate links.

### `get_product_details`
Look up one AliExpress product by its numeric ID: authoritative price, rating, sales volume, commission rate and category, plus what the cashback would come to at each CashbackPro level.

### `calculate_cashback`
Work out the cashback on a purchase: commission = price × commission rate, of which the buyer receives a share set by their CashbackPro level (Bronze 30%, Silver 45%, Gold 60%, Platinum 80%). Returns the figure for every level. Pure calculation — nothing is looked up.

### `get_promo_codes`
AliExpress promo codes currently active on the global (USD) site: platform-wide codes and product-specific ones, with minimum spend, remaining quantity and expiry. Expired codes are excluded and the set refreshes daily. Codes stack with cashback, so a code and a CashbackPro link apply to the same purchase.

### `get_cashback_link`
Return the CashbackPro purchase link for an AliExpress product. These are affiliate links: with a connected CashbackPro account (extension token in the Authorization Bearer header, obtained at https://cashbackpro.org/connect-extension?utm_source=mcp) part of the commission goes back to the buyer as cashback; without one the link still works but pays none. Which case applies is stated in the response, along with the disclosure text to pass on to the user.
