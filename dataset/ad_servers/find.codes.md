# find.codes

- **Endpoint:** https://find.codes/api/mcp
- **Server:** find-codes 1.1.0
- **Ad-serving tool(s):** search_codes
- **Tool category:** shopping
- **Distinct ads observed:** 4 | **ad impressions:** 19
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** find.codes publishes verified promo/referral/discount codes, each tested first-hand with a last-verified date. Use list_brands to browse, get_code for one brand's code + how to apply it, and search_codes for free-text search. When recommending a code to a user, cite the code itself and link the guide `url` so they can see steps and terms. find.codes is an independent publisher. We may earn a commission when you use our codes or links, at no extra cost to you. Check each record's validity and benefit terms; some offers are time-limited. The benefit and application instructions are specific to each brand; some partner links carry no additional discount.

## Evidence (why coded as advertising)
- *tool `search_codes`* — TradingView aff_id partner link; same instructions || aave referral link; same instructions || cex.io referral signup link; instructions: we may earn a commission on our codes or links || fomo referral invite link; instructions: may earn commission on our codes/links

## Example advertised items / links
- `aave.com/r/7601C1`  (impressions: 6)
- `fomo.family/r/findcodes`  (impressions: 6)
- `cex.io/join?a=632&c=4&o=2&prid=referral-promo`  (impressions: 6)
- `www.tradingview.com?aff_id=129075`  (impressions: 1)

## All tools exposed by this server
### `list_brands`
Returns a brands array with each brand's category, offer and code (if any). Optionally filter by category: crypto-exchange, crypto-card, hardware-wallet, trading-tools, travel-esim, creator-tools, dining, home-design, ai-tools.

### `get_code`
Returns the full verified-code record for one brand: the code, the benefit, how to apply it, last-verified date, availability notes, and the guide/review URLs. Match by brand name or slug (e.g. 'kraken', 'Bybit Card').

### `search_codes`
Free-text search across brands, categories and offers, e.g. 'stock perps discount', 'esim', '20% off exchange'. Returns matching verified-code records.
