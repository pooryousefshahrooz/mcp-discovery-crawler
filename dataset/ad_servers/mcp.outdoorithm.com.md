# mcp.outdoorithm.com

- **Endpoint:** https://mcp.outdoorithm.com/mcp
- **Server:** outdoorithm 0.1.0
- **Ad-serving tool(s):** search_gear
- **Tool category:** shopping
- **Distinct ads observed:** 25 | **ad impressions:** 250
- **Coder confidence / basis:** medium / in_response_trace
- **Server instructions:** 
    Outdoorithm MCP Server - Campground discovery and trip planning tools.

    This server provides 13 tools for discovering campgrounds, checking availability,
    preparing reservation handoffs, weather, safety, gear, and planning camping trips
    across the US. Data comes from Outdoorithm's database of 10,000+ campgrounds with
    enriched reviews, sentiment analysis, community safety scores, and gear
    recommendations.

    Every tool here is read-only and needs no credentials. Nothing on this server
    changes state or asks the user for a key.

    CAMPGROUND TOOLS:
    - search_campgrounds: Search with 40+ filters (location, amenities, activities, safety, terrain)
    - get_campground_details: Full campground profile with ~80 curated fields
    - find_similar_campgrounds: Vecto

## Evidence (why coded as advertising)
- *tool `search_gear`* — Amazon tag in affiliate_links field || REI Impact link in affiliate_links field || REI Impact link in server field affiliate_links on 'Our Pick' catalogue items

## Example advertised items / links
- `www.amazon.com/dp/B01MY7S3H8?tag=outdoorithm00-20`  (impressions: 10)
- `www.rei.com/product/181227/ruffwear-grip-trex-dog-boots-pair`  (impressions: 10)
- `www.amazon.com/dp/B0CT62VV1X?tag=outdoorithm00-20`  (impressions: 10)
- `www.rei.com/product/2294430004`  (impressions: 10)
- `www.amazon.com/dp/B08LP2PQ6C?tag=outdoorithm00-20`  (impressions: 10)
- `www.rei.com/product/2294450003`  (impressions: 10)
- `www.rei.com/product/C08309/deuter-kid-comfort-pro-child-carrier?sku=C083090001`  (impressions: 10)
- `www.rei.com/product/2375410002`  (impressions: 10)
- `www.amazon.com/dp/B0CT617HFM?tag=outdoorithm00-20`  (impressions: 10)
- `www.amazon.com/dp/B0DFGMTVP8?tag=outdoorithm00-20`  (impressions: 10)
- `www.amazon.com/dp/B08FF8JQDS?tag=outdoorithm00-20`  (impressions: 10)
- `www.amazon.com/dp/B00DT8RYCM?tag=outdoorithm00-20`  (impressions: 10)
- `www.amazon.com/dp/B0CYZZ87GK?tag=outdoorithm00-20`  (impressions: 10)
- `www.amazon.com/dp/B07MRG47WC?tag=outdoorithm00-20`  (impressions: 10)
- `www.rei.com/product/1501920001`  (impressions: 10)
- … and 10 more (see analysis/ad_provenance/out/ad_items.csv)

## All tools exposed by this server
### `build_packing_list`
Generate a context-aware packing checklist for a camping trip.  Returns categorized items from the gear catalog, adjusted for campground amenities, activities, weather, and group size.

### `calculate_drive_times`
Calculate realistic drive times from an origin to multiple campgrounds using Mapbox routing with live traffic.  Uses the Mapbox Matrix API for traffic-aware routing. Maximum 9 destinations per request.

### `check_availability`
Check real-time campground availability for specific dates.  Queries the camply-service to check live campsite availability against reservation systems. Supports 30+ providers including RecreationDotGov, ReserveCalifornia, state parks, and county parks.

### `check_safety`
Check campgrounds for safety issues, community atmosphere, and active alerts.  Checks: - Greenbook community safety (vibe scores, discrimination reports, flag status) - Active campground alerts (closures, restrictions) from enriched data - Red flag detection (prevents recommending unsafe campgrounds)

### `compare_gear`
Compare 2-3 gear items side-by-side with specs, pros/cons, verdicts, and comparison summary.  Supports lookup by unique_id with slug fallback.

### `get_weather`
Get camping-specific 7-day weather forecast with suitability ratings and gear recommendations.  Uses Open-Meteo's commercial API to provide: - Daily high/low temps, conditions, precipitation, wind - Camping suitability rating per day (excellent/good/fair/poor/not_recommended) - Gear recommendations based on conditions - Safety warnings for extreme weather - Best camping days in the forecast period  Forecast data is from Open-Meteo, licensed under CC BY 4.0. Every successful forecast includes an `attribution` field carrying the required credit.

### `find_similar_campgrounds`
Find campgrounds similar to a given campground using vector embedding similarity.  Uses pre-computed embeddings combining review text (semantic) and structured attributes (amenities, terrain, activities) for nuanced similarity matching.

### `get_campground_details`
Get comprehensive details for a specific campground including amenities, reviews, safety, and seasonal ratings.  Returns ~80 curated fields (not the raw 214-column dump) including: - Identity, location, fees, site info - All amenity and activity booleans + descriptions - Review summaries, best campsites, common complaints, tips - Greenbook community safety (vibe score, flag status) - Seasonal LLM ratings (spring/summer/fall/winter) - Sentiment trend direction - Hero image with credits  Data coverage: a missing or empty field means the attribute isn't in our records, not that the feature is absent at the campground. Coverage varies by provider; the campground operator is the authoritative source.

### `get_gear_for_campground`
Get personalized gear recommendations for a specific campground.  Returns pre-computed recommendations across slot types: essential (must-have), activity (activity-matched), comfort (nice-to-have), amenity_gap (compensates for missing amenities). Each includes product details and purchase links.

### `prepare_reservation`
Prepare a one-tap booking handoff for the user's chosen campground/dates.  Returns a pre-filled deep link to the operator's reservation page plus the booking-window context (release date/time, operator rules, alert suggestion). Does NOT book on behalf: third-party booking is prohibited by Recreation.gov, ReserveCalifornia, ReserveAmerica, and every other supported public-land operator.

### `search_campgrounds`
Search for campgrounds with 40+ filters including location, amenities, activities, and community safety.  Requires at least one location constraint: near_location, campground_name, latitude+longitude, or states.

### `search_gear`
Search the Outdoorithm gear catalog by keyword, category, price range, kit, necessity, or recommendation tier.  Returns matching products with prices, verdicts, and purchase links.

### `health_check`
Check server health and connectivity.  Returns:     Dictionary with health status including:     - status: "healthy" or "unhealthy"     - version: Server version     - environment: Current environment (dev/staging/prod)
