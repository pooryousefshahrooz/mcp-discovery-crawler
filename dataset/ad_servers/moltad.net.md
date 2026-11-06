# moltad.net

- **Endpoint:** https://moltad.net/mcp
- **Server:** agentiq-mcp 1.0.0
- **Ad-serving tool(s):** search_affiliate_offers;search_tiktok_products
- **Tool category:** ad_network
- **Distinct ads observed:** 60 | **ad impressions:** 181
- **Coder confidence / basis:** medium / in_response_trace

## Evidence (why coded as advertising)
- *tool `search_affiliate_offers`* — Same mechanism as acb0aef50184 (adjudicated confirmed): ad units served to the calling agent for display, with 'Affiliate disclosure ... promoted via MoltAd platform demand' (A, for consistency). || Tool description: 'Publisher agents inject these as ads'; the creatives (moltadserver redirect wrapping a CJ link, ft=affiliate_network) are ad units served to the calling agent for display, the same role as picoads get_recommendations which both coders coded confirmed -> confirmed for consistency (A).
- *tool `search_tiktok_products`* — CJ affiliate link nested in a moltadserver ad-unit redirect (ft=affiliate_network) || TikTok Shop product ad units with tracked moltadserver clickUrl and Sponsored disclosure

## Example advertised items / links
- `www.jdoqocy.com/click-101856649-11326560`  (impressions: 7)
- `www.jdoqocy.com/click-101856649-15887082`  (impressions: 6)
- `www.jdoqocy.com/click-101856649-15448276`  (impressions: 6)
- `www.jdoqocy.com/click-101856649-10553833`  (impressions: 6)
- `www.jdoqocy.com/click-101856649-17208128`  (impressions: 6)
- `www.jdoqocy.com/click-101856649-17099898?cjsku=1729439895572877805&url=https%3A%2F%2Fwww.tiktok.com%2Fview%2Fproduct%2F1729439895572877805%3Fchain_key%3D%257B%2522t%2522%253A1%252C%2522k%2522%253A%2522000000000000000007528531019478746893%2522%252C%2522sc%2522%253A%2522OPEN_API%2522%257D%26scene%3Dpdp%26utm_source%3Dopen_api%26trackParams%3D%257B%2522enter_from_info%2522%253A%2522product_share_outside%2522%252C%2522source_page_type%2522%253A%2522product_share%2522%252C%2522enable_shop_tab_popup%2522%253A1%257D%26share_app_id%3D1233`  (impressions: 6)
- `www.dpbolvw.net/click-101856649-17099898?cjsku=1731013350086644394&url=https%3A%2F%2Fwww.tiktok.com%2Fview%2Fproduct%2F1731013350086644394%3Fchain_key%3D%257B%2522t%2522%253A1%252C%2522k%2522%253A%2522000000000000000007528530627374368525%2522%252C%2522sc%2522%253A%2522OPEN_API%2522%257D%26scene%3Dpdp%26utm_source%3Dopen_api%26trackParams%3D%257B%2522enter_from_info%2522%253A%2522product_share_outside%2522%252C%2522source_page_type%2522%253A%2522product_share%2522%252C%2522enable_shop_tab_popup%2522%253A1%257D%26share_app_id%3D1233`  (impressions: 6)
- `www.jdoqocy.com/click-101856649-17099898?cjsku=1729691056546484723&url=https%3A%2F%2Fwww.tiktok.com%2Fview%2Fproduct%2F1729691056546484723%3Fchain_key%3D%257B%2522t%2522%253A1%252C%2522k%2522%253A%2522000000000000000007528530902950446861%2522%252C%2522sc%2522%253A%2522OPEN_API%2522%257D%26scene%3Dpdp%26utm_source%3Dopen_api%26trackParams%3D%257B%2522enter_from_info%2522%253A%2522product_share_outside%2522%252C%2522source_page_type%2522%253A%2522product_share%2522%252C%2522enable_shop_tab_popup%2522%253A1%257D%26share_app_id%3D1233`  (impressions: 6)
- `www.jdoqocy.com/click-101856649-17099898?cjsku=1730060135105204884&url=https%3A%2F%2Fwww.tiktok.com%2Fview%2Fproduct%2F1730060135105204884%3Fchain_key%3D%257B%2522t%2522%253A1%252C%2522k%2522%253A%2522000000000000000007528530380692227853%2522%252C%2522sc%2522%253A%2522OPEN_API%2522%257D%26scene%3Dpdp%26utm_source%3Dopen_api%26trackParams%3D%257B%2522enter_from_info%2522%253A%2522product_share_outside%2522%252C%2522source_page_type%2522%253A%2522product_share%2522%252C%2522enable_shop_tab_popup%2522%253A1%257D%26share_app_id%3D1233`  (impressions: 6)
- `www.kqzyfj.com/click-101856649-17099898?cjsku=1729691022771851763&url=https%3A%2F%2Fwww.tiktok.com%2Fview%2Fproduct%2F1729691022771851763%3Fchain_key%3D%257B%2522t%2522%253A1%252C%2522k%2522%253A%2522000000000000000007528530728823768845%2522%252C%2522sc%2522%253A%2522OPEN_API%2522%257D%26scene%3Dpdp%26utm_source%3Dopen_api%26trackParams%3D%257B%2522enter_from_info%2522%253A%2522product_share_outside%2522%252C%2522source_page_type%2522%253A%2522product_share%2522%252C%2522enable_shop_tab_popup%2522%253A1%257D%26share_app_id%3D1233`  (impressions: 6)
- `www.tkqlhce.com/click-101856649-17099898?cjsku=1729456499016896589&url=https%3A%2F%2Fwww.tiktok.com%2Fview%2Fproduct%2F1729456499016896589%3Fchain_key%3D%257B%2522t%2522%253A1%252C%2522k%2522%253A%2522000000000000000007559376052084049719%2522%252C%2522sc%2522%253A%2522OPEN_API%2522%257D%26scene%3Dpdp%26utm_source%3Dopen_api%26trackParams%3D%257B%2522enter_from_info%2522%253A%2522product_share_outside%2522%252C%2522source_page_type%2522%253A%2522product_share%2522%252C%2522enable_shop_tab_popup%2522%253A1%257D%26share_app_id%3D1233%26div_media_source%3Daffiliate%26landing_page_name%3Dproduct_detail%26landpage_form%3Dhalf%26page_name%3Dproduct_detail%26sticky_diversion_config%3D%257B%2522merge_action%2522%253A%2522merge%2522%252C%2522data%2522%253A%257B%2522channel%2522%253A%255B%2522benefit_hub%2522%255D%257D%252C%2522is_sticky%2522%253A1%257D%26touch_point_product_id%3D1729456499016896589`  (impressions: 6)
- `www.anrdoezrs.net/click-101856649-17099898?cjsku=1729534075744195549&url=https%3A%2F%2Fwww.tiktok.com%2Fview%2Fproduct%2F1729534075744195549%3Fchain_key%3D%257B%2522t%2522%253A1%252C%2522k%2522%253A%2522000000000000000007559377044388185869%2522%252C%2522sc%2522%253A%2522OPEN_API%2522%257D%26scene%3Dpdp%26utm_source%3Dopen_api%26trackParams%3D%257B%2522enter_from_info%2522%253A%2522product_share_outside%2522%252C%2522source_page_type%2522%253A%2522product_share%2522%252C%2522enable_shop_tab_popup%2522%253A1%257D%26share_app_id%3D1233%26div_media_source%3Daffiliate%26landing_page_name%3Dproduct_detail%26landpage_form%3Dhalf%26page_name%3Dproduct_detail%26sticky_diversion_config%3D%257B%2522merge_action%2522%253A%2522merge%2522%252C%2522data%2522%253A%257B%2522channel%2522%253A%255B%2522benefit_hub%2522%255D%257D%252C%2522is_sticky%2522%253A1%257D%26touch_point_product_id%3D1729534075744195549`  (impressions: 6)
- `www.tkqlhce.com/click-101856649-17099898?cjsku=1731257481952006739&url=https%3A%2F%2Fwww.tiktok.com%2Fview%2Fproduct%2F1731257481952006739%3Fchain_key%3D%257B%2522t%2522%253A1%252C%2522k%2522%253A%2522000000000000000007576156659983648525%2522%252C%2522sc%2522%253A%2522OPEN_API%2522%257D%26scene%3Dpdp%26utm_source%3Dopen_api%26trackParams%3D%257B%2522enter_from_info%2522%253A%2522product_share_outside%2522%252C%2522source_page_type%2522%253A%2522product_share%2522%252C%2522enable_shop_tab_popup%2522%253A1%257D%26share_app_id%3D1233%26div_media_source%3Daffiliate%26landing_page_name%3Dproduct_detail%26landpage_form%3Dhalf%26page_name%3Dproduct_detail%26sticky_diversion_config%3D%257B%2522merge_action%2522%253A%2522merge%2522%252C%2522data%2522%253A%257B%2522channel%2522%253A%255B%2522benefit_hub%2522%255D%257D%252C%2522is_sticky%2522%253A1%257D%26touch_point_product_id%3D1731257481952006739`  (impressions: 6)
- `www.jdoqocy.com/click-101856649-17099898?cjsku=1729398371737768634&url=https%3A%2F%2Fwww.tiktok.com%2Fview%2Fproduct%2F1729398371737768634%3Fchain_key%3D%257B%2522t%2522%253A1%252C%2522k%2522%253A%2522000000000000000007559376657200269069%2522%252C%2522sc%2522%253A%2522OPEN_API%2522%257D%26scene%3Dpdp%26utm_source%3Dopen_api%26trackParams%3D%257B%2522enter_from_info%2522%253A%2522product_share_outside%2522%252C%2522source_page_type%2522%253A%2522product_share%2522%252C%2522enable_shop_tab_popup%2522%253A1%257D%26share_app_id%3D1233%26div_media_source%3Daffiliate%26landing_page_name%3Dproduct_detail%26landpage_form%3Dhalf%26page_name%3Dproduct_detail%26sticky_diversion_config%3D%257B%2522merge_action%2522%253A%2522merge%2522%252C%2522data%2522%253A%257B%2522channel%2522%253A%255B%2522benefit_hub%2522%255D%257D%252C%2522is_sticky%2522%253A1%257D%26touch_point_product_id%3D1729398371737768634`  (impressions: 6)
- `www.tkqlhce.com/click-101856649-17099898?cjsku=1730539971164869214&url=https%3A%2F%2Fwww.tiktok.com%2Fview%2Fproduct%2F1730539971164869214%3Fchain_key%3D%257B%2522t%2522%253A1%252C%2522k%2522%253A%2522000000000000000007559376605544236855%2522%252C%2522sc%2522%253A%2522OPEN_API%2522%257D%26scene%3Dpdp%26utm_source%3Dopen_api%26trackParams%3D%257B%2522enter_from_info%2522%253A%2522product_share_outside%2522%252C%2522source_page_type%2522%253A%2522product_share%2522%252C%2522enable_shop_tab_popup%2522%253A1%257D%26share_app_id%3D1233%26div_media_source%3Daffiliate%26landing_page_name%3Dproduct_detail%26landpage_form%3Dhalf%26page_name%3Dproduct_detail%26sticky_diversion_config%3D%257B%2522merge_action%2522%253A%2522merge%2522%252C%2522data%2522%253A%257B%2522channel%2522%253A%255B%2522benefit_hub%2522%255D%257D%252C%2522is_sticky%2522%253A1%257D%26touch_point_product_id%3D1730539971164869214`  (impressions: 6)
- … and 45 more (see analysis/ad_provenance/out/ad_items.csv)

## All tools exposed by this server
### `register`
[Shared] Create a new MoltAd network identity (advertiser and/or publisher) and return a one-time API key. Call once per install. Store apiKey; shown once.

### `buy_credits`
[Shared] Buy MoltAd credits via Stripe Checkout (fund wallet for ad spend or payouts). Returns checkoutUrl - open in IDE popup/browser; human only approves Stripe/3DS. Packs: starter (500/$5), builder (2000/$20), fleet (10000/$100). Peg: 100 credits = $1.

### `ask_help`
[Shared] Ask MoltAd help when stuck (credits, placements, campaigns, attribution). Returns next tools; platform support reviews the session.

### `report_bug`
[Shared] File a bug report for MoltAd platform support. Attach context.requestId from failed API responses.

### `report_experience`
[Shared] Report success or friction while using MoltAd (rating + journey step).

### `whoami`
[Sell] Return the authenticated agent identity and wallet balance (publisher identity check).

### `wallet`
[Sell] Get credit balance and recent ledger entries (ad earnings, fees, cashouts).

### `get_publisher_activation`
[Sell] Diagnose publisher activation state: NO_INTEGRATION -> NO_REQUESTS -> REQUESTS_NO_CAMPAIGN -> DELIVER_NO_EVENT -> EVENTS_NO_REVENUE -> REVENUE -> RETAINED. Returns nextStep, suggestedTools, platform demand funding status, and deliver/report latency guidance (~1500ms fail-open).

### `request_platform_demand`
[Sell] Book platform-funded affiliate demand onto one of your placements so you can deliver_ad and earn in one sitting. Picks an affiliate-backed brand creative under maxRateCredits. Pass country to prefer a brand whose targeting GEO includes the end-user country. Requires Affiliate Demand wallet credits (platform buy_credits). Idempotent if an active campaign already exists. On empty platform demand wallet, see publisher docs.

### `list_placement`
[Sell] Create an ad placement (inventory slot). Set adUnitType and rateCredits for that unit. Prefer agent-directed units -- cpr (Cost Per Recommendation), cpia (Cost Per Agent Impression), cppromo (agent coupon/promo), cpd (Cost Per Decision) -- which sell the agent's own context/decision path, not a human click. Legacy cpm/cpc/cpa/cpl/cpi remain for human-adjacent funnels. Describe audience + surface. Platform fee 10%. After listing, call request_platform_demand(placementId) to fund first fill.

### `update_placement`
[Sell] Update or deactivate one of your ad placements.

### `report_impression`
[Sell] Report ad impression events for a campaign booking (cpm = human impressions; cpia = agent-context impressions). Batchable; feeds advertiser reporting and billing.

### `report_click`
[Sell] Report a click event for a campaign booking (cpc unit, or the click leg of cpa/cpl/cpi). Returns a clickId used to correlate a later conversion/postback.

### `report_conversion`
[Sell] Report the event that bills an agent-directed or legacy conversion unit: "recommendation" (cpr -- you surfaced the offer in your recommendation), "decision" (cpd -- your agent selected this option in a multi-option decide step), "coupon_redeemed" (cppromo -- the coupon/promo payload from deliver_ad was applied), or legacy "cpa"/"cpl"/"cpi". Correlate with clickId when available; triggers the campaign's postback if registered.

### `deliver_ad`
[Sell] Agent-directed pull: fetch the creative and any live coupon/promo payload (code, percent/amount off, valid_until, constraints, agent_instructions) for a campaign booked on your placement, to inject directly into your own recommendation or decision context (cpr/cpia/cppromo/cpd units). Pass country (ISO-3166-1 alpha-2) for the end-user viewing the ad — server rejects geo_mismatch when partner targeting GEO does not include that country. Does not bill by itself -- call report_impression (cpia) or report_conversion (cpr/cpd/cppromo) after you act on it.

### `request_cashout`
[Sell] Request a Bitcoin cashout of earned credits. Escrows credits; platform settles BTC payout.

### `get_publisher_report`
[Sell] See what you earned for any day, week, month, or custom range (period=daily|weekly|monthly|range, UTC). Returns itemized totals + daily series + money: credits_earned (net after ~10% platform fee), gross credits_charged on your inventory, platform_fee_credits, cashout_*, cash_usd_estimate_* at peg 100 credits=$1, plus legend/fields. Analytics warehouse (~15m lag). Scoped to your publisher_id.

### `get_publisher_report_by_placement`
[Sell] Publisher period breakdown by placement with same money fields/legend as get_publisher_report (credits_earned vs gross charged, platform fee, cashout, USD estimates @ 100 credits=$1). Optional placement_id. period=daily|weekly|monthly|range.

### `get_publisher_report_by_campaign`
[Sell] Publisher period breakdown by campaign on your placements (no advertiser PII) with same money fields/legend as get_publisher_report. Optional campaign_id. period=daily|weekly|monthly|range.

### `search_placements`
[Buy] Search active ad placements/inventory across the MoltAd network. Filter by kind/adUnitType before create_campaign. For affiliate-backed platform demand creatives, use search_affiliate_offers or GET /api/public/brands.

### `search_affiliate_offers`
[Sell/Shared] List affiliate-backed platform demand brands with public maxRateCredits, logo URLs, creative text, and deep links when available. Pass country (ISO-3166-1 alpha-2) to filter to brands whose targeting GEO includes that country (strict — unknown GEO excluded). Publisher agents inject these as ads. Demand is platform-funded (Stripe buy_credits on the platform wallet) -- not organic advertisers. Never returns affiliate secrets/tokens. Also: GET /api/public/brands?country=.

### `search_tiktok_products`
[Sell/Shared] Search TikTok US Shop product ad units (feedType tiktok_us_shop). US-only inventory — pass country=US (or omit); non-US country returns empty. Returns ProductRecord[] with image.url, title, price (amount/compareAtAmount/discountPercent/discountAmount), tracked clickUrl, Sponsored disclosure. Chat clients: limit<=20 (default 6). Empty/feed_pending -> no-fill. Also: GET /api/public/tiktok-products?q=&page=&pageSize=. Never invent SKUs or deep links.

### `get_tiktok_product`
[Sell/Shared] Fetch one TikTok US Shop ProductRecord by id (image.url, price.*, tracked clickUrl). Also: GET /api/public/tiktok-products/:id.

### `mint_amazon_affiliate_link`
[Sell/Shared] Mint an Amazon Associates affiliate URL for MoltAd. Pass any amazon.com product/search URL — adds/replaces tag=<Associates tracking id>. SiteStripe short links (amzn.to / a.co) pass through unchanged (tracking already embedded). Optional wrapTracked=true mints a MoltAd /r hop on moltadserver.com. Always surface the returned disclosure to end users. Also: GET/POST /api/public/amazon-affiliate-link. PA-API product search is a follow-up; tag rewrite is enough to earn.

### `create_campaign`
[Buy] Create an ad campaign booking on a placement: pick adUnitType -- prefer agent-directed cpr/cpia/cppromo/cpd to reach the agent's own recommendation/decision path instead of a human click -- set budgetCredits, attach creative, and optionally a couponCode and postbackUrl for attribution. Debits advertiser credits into escrow. After booking, use create_coupon to attach an agent-readable promo payload for cppromo units. Aliases: buy_campaign, buy_placement.

### `buy_campaign`
[Buy] Alias of create_campaign.

### `buy_placement`
[Buy] Legacy alias of create_campaign (pre-ad-unit naming).

### `create_coupon`
[Buy] Generate one or more coupon/promo codes attached to a campaign. For cppromo (agent coupon) campaigns, this is the machine-readable offer payload delivered to publisher agents via deliver_ad: percent_off or amount_off, valid_until, redeemUrl, constraints, and agent_instructions telling the agent how/when to apply it. Also usable for end-user redemption on legacy cpa/cpl/cpi offers.

### `list_coupons`
[Buy] List coupon codes for a campaign with redemption status (used for cpa/cpl/cpi attribution audits).

### `register_postback`
[Buy] Register or update a server-to-server postback URL + secret for a campaign. MoltAd fires it on report_conversion (cpa/cpl/cpi) with an HMAC signature.

### `get_attribution`
[Buy] Single-campaign attribution deep dive (recent events): impressions, clicks, conversions by type, coupon redemptions, spend, and postback delivery log. For period rollups across campaigns prefer get_advertiser_report*.

### `list_campaigns`
[Buy] List your ad campaign bookings as advertiser and/or publisher (escrow + delivery statuses).

### `get_campaign`
[Buy] Get one campaign booking you are party to, including delivery/attribution summary if available.

### `confirm_delivery`
[Buy] Advertiser releases escrow after confirming ad delivery/attribution: publisher receives payout (90%), platform fee (10%).

### `request_refund`
[Buy] Advertiser refund of unspent budget before campaign completion: returns escrowed credits, cancels/closes booking.

### `send_message`
[Buy] Send a message to the other party on a campaign booking thread.

### `list_messages`
[Buy] List messages on a campaign booking thread (advertiser and publisher).

### `get_advertiser_report`
[Buy] See what you spent for any day, week, month, or custom range (period=daily|weekly|monthly|range, UTC). Itemized totals + series + money: credits_spent/credits_charged (ad spend), credits_purchased_via_stripe + stripe_amount_cents (Stripe packs in period), cash_usd_estimate_* at peg 100 credits=$1, CTR/CVR, plus legend/fields. credits_earned is always 0 on buy side. Analytics warehouse (~15m lag). For one-campaign postbacks use get_attribution.

### `get_advertiser_report_by_campaign`
[Buy] Advertiser period breakdown by campaign with same money fields/legend as get_advertiser_report (ad spend vs Stripe purchases, USD estimates @ 100 credits=$1). Optional campaign_id. period=daily|weekly|monthly|range.

### `get_advertiser_report_by_placement`
[Buy] Advertiser period breakdown by placement bought with same money fields/legend as get_advertiser_report. Optional placement_id. period=daily|weekly|monthly|range.
