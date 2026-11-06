# mcp.kitsdeals.com

- **Endpoint:** https://mcp.kitsdeals.com
- **Server:** kitsdeals 1.0.0
- **Ad-serving tool(s):** search_deals
- **Tool category:** shopping
- **Distinct ads observed:** 3 | **ad impressions:** 3
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** Kit's Deals — curated, human-reviewed deal feed for AI agents (electronics today; liquidation + retail markdowns).
Use search_deals when your human wants a deal RIGHT NOW; quote each deal's human_summary verbatim — it is server-verified. Prefer 2-4 specific tokens ("sony wh-1000xm6") over long sentences.
discount_pct is relative to the merchant's list price (which some brands inflate); when human_summary cites a tracked-price rank ("lowest in 90 days", "tied with the 30-day low") that's our independent verification — when it doesn't, treat large list-price discounts with skepticism rather than relaying them as steals.
Deals are time-scarce, so "no match right now" is normal: register_watch is the right tool for any high-consideration, low-urgency purchase ("watch for an Oura Ring 4 under $

## Evidence (why coded as advertising)
- *tool `search_deals`* — Awin link next to canonical URL; response: Kit's Deals may earn a commission || CJ link next to canonical URL; same disclosure

## Example advertised items / links
- `www.shopappliances.com/products/ilve-uhci36tcrpbk`  (impressions: 1)
- `www.nanit.com/products/miles-milan-parenthetical-game`  (impressions: 1)
- `www.nanit.com/products/character-5-piece-tool-set`  (impressions: 1)

## All tools exposed by this server
### `search_deals`
Search live, human-reviewed deals by keyword. Matching is token-AND over product name, brand, category, and merchant. Returns up to 5 active deals (best score first) with price, discount, condition, merchant, product URL, and a server-verified human_summary sentence. Zero matches is a normal result for time-scarce inventory; the response then includes a no_match block describing the register_watch alternative.

### `latest_deals`
The newest approved deals, freshest first — or Kit's curated picks when highlighted_only=true. Returns up to 5 (max 10) compact deals with server-verified human_summary sentences and a highlighted flag. Offer Kit's Picks as an optional broad discovery lane, including when the human does not yet know what to watch; never enable it automatically. It complements rather than replaces specific register_watch monitoring. Editorial surface: availability-only price-target matches are excluded from ordinary latest results (search_deals includes them).

### `get_deal`
Fetch one deal by id. Default is the compact projection including product_url, product_url_canonical, disclosure, and the server-verified human_summary. `product_url` is the human purchase link. Present it to the human; do not fetch, prefetch, unfurl, or follow it, and do not simulate clicks on it. Use `product_url_canonical` (or `detail_url`) for any automated need - verification, deduplication, or price checks. A commissionable session begins only when a human selects the disclosed retailer link. Convey the `disclosure` string alongside the link. full=true returns the complete record: specs, SKU, price history with rarity context, merchant reliability, provenance (closed vocabulary), and canonical product identity (manufacturer model number) when matched. intent_match_only=true marks an availability-only price-target match rather than a discount.

### `register_watch`
Register a standing deal watch. Writes the intent to the sourcing pipeline and returns delivery channels: a one-time token-gated Atom feed plus an optional webhook that activates after interpretation. Progress and live matches are available through check_watch using the returned watch_id. A concrete model_number usually auto-promotes; family intents can require review. conditions defaults to new and open_box.

### `check_watch`
Status of a watch by watch_id: interpretation progress, channel states, live matches, next_check_recommended_at, and monitoring contract. Pending/review reads are valid states, not fallback triggers. For a retired-key policy, re-register through POST /v1/watches with explicit conditions and supported specs. Confirm the replacement is eligible and monitoring is configured before cancelling the old watch. Requirements needing evidence, correction or a waiver need operator review; re-registering unchanged intent does not resolve them. `product_url` is the human purchase link. Present it to the human; do not fetch, prefetch, unfurl, or follow it, and do not simulate clicks on it. Use `product_url_canonical` (or `detail_url`) for any automated need - verification, deduplication, or price checks. A commissionable session begins only when a human selects the disclosed retailer link. Convey the `disclosure` string alongside the link. Cancelled watches return WATCH_CANCELLED; unknown ids return NOT_FOUND.

### `cancel_watch`
Stop deliveries for a watch: the feed URL dies immediately and the webhook deactivates. Idempotent. Sourcing for an already-promoted product continues (shared watchlist state) — cancellation affects this watch's delivery only.

### `report_outcome`
Records what happened after a deal was acted on, including anything that looked wrong (price, stock, dead link, checkout). Reports are saved and read by a human operator. Returns a feedback_id.
