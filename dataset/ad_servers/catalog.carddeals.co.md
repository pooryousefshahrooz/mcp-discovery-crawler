# catalog.carddeals.co

- **Endpoint:** https://catalog.carddeals.co/mcp
- **Server:** co.carddeals/deals 1.0.0
- **Ad-serving tool(s):** search_gift_card_deals
- **Tool category:** shopping
- **Distinct ads observed:** 8 | **ad impressions:** 44
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** Use these read-only tools to find current U.S. gift-card discounts. Always preserve the returned seller conditions, affiliate disclosure, timestamps, and freshness warning. Never claim a purchase was completed; these tools only return links.

## Evidence (why coded as advertising)
- *tool `search_gift_card_deals`* — own-host deal redirect with 'Relationship: affiliate' per offer || same offers as 7d7749a1fe75 ('Relationship: affiliate')

## Example advertised items / links
- `catalog.carddeals.co/v1/deals/go/offer%3Abest-western%3Acardcash%3Aonline`  (impressions: 6)
- `catalog.carddeals.co/v1/deals/go/offer%3Abest-western%3Acarddepot%3Aother`  (impressions: 6)
- `catalog.carddeals.co/v1/deals/go/offer%3Abest-buy%3Aarbitragecard%3Aonline`  (impressions: 6)
- `catalog.carddeals.co/v1/deals/go/offer%3Abest-buy%3Acardcash%3Aonline`  (impressions: 6)
- `catalog.carddeals.co/v1/deals/go/offer%3Abest-western%3Acardcenter%3Aonline`  (impressions: 6)
- `catalog.carddeals.co/v1/deals/go/offer%3Abest-buy%3Acarddepot%3Aother`  (impressions: 6)
- `catalog.carddeals.co/v1/deals/go/offer%3Abest-buy%3Acardcenter%3Aonline`  (impressions: 6)
- `catalog.carddeals.co/v1/deals/go/offer%3Abest-buy%3Acardcookie%3Aother`  (impressions: 2)

## All tools exposed by this server
### `search_gift_card_deals`
Use this when the user wants to discover or compare current U.S. gift-card discounts across brands or within a category. Returns structured provider offers and current destination links. Do not use it for an exact single brand when get_gift_card_deals can return the complete provider set.

### `lookup_gift_card_deals`
Use this when the user supplies up to 10 exact CardDeals product IDs or brand slugs to compare in one call. Product IDs use the form brand:starbucks. Do not use it for fuzzy discovery; use search_gift_card_deals instead. Unknown IDs are returned in not_found instead of being guessed.

### `get_gift_card_deals`
Use this when the user asks for complete current provider details for one exact gift-card brand. Accepts a brand slug, product ID such as brand:starbucks, or exact brand name. Do not use it for broad category discovery. Returns no purchase action—only current provider or CardDeals checkout links.
