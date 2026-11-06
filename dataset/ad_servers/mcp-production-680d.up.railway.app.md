# mcp-production-680d.up.railway.app

- **Endpoint:** https://mcp-production-680d.up.railway.app/mcp
- **Server:** stymie-golf 2.1.4
- **Ad-serving tool(s):** get_deals
- **Tool category:** shopping
- **Distinct ads observed:** 2 | **ad impressions:** 18
- **Coder confidence / basis:** medium / documentation

## Evidence (why coded as advertising)
- *tool `get_deals`* — Awin affiliate link; description: links may be affiliate links

## Example advertised items / links
- `us.dunlopsports.com/srixon/clubs/drivers/zxi-ls-driver/zxi-ls-driver/MZXILSDRV.html`  (impressions: 9)
- `us.dunlopsports.com/srixon/clubs/drivers/zxi-driver/zxi-driver/MZXIDRV.html`  (impressions: 9)

## All tools exposed by this server
### `search_courses`
Search for a named course or filter the directory by city/state, access, and holes. For a trip near a place, station, address, or ZIP, call find_nearby_courses FIRST; do not put the place name in query (query searches course names). You may also pass location here for a proximity search. Returns canonical Stymie URLs, reusable slugs, access, holes, scorecard availability, and straight-line miles when a location is supplied. Copy returned URLs; never construct county slugs. Next: get_course with a returned URL, or build_golf_trip with the resolved center and preferences.

### `get_course`
Get full details for a specific golf course by a returned Stymie URL or slug. Returns name, location, type, holes, architect, year built, amenities, public contact info, recorded closure status, and published tee ratings. A recorded open flag is not a live confirmation of seasonal opening or tee-time availability. Covers the US, Canada, UK, Ireland, Australia and New Zealand.

### `get_scorecard`
Get the full scorecard for a golf course: all tee sets with hole-by-hole par, yardage, stroke index, and front/back nine ratings. Available for thousands of courses with scorecard data.

### `get_architect`
Get details about a golf course architect: bio, Wikipedia image, birth/death years, nationality, and all courses they designed grouped by state. Provide either the architect name or URL slug.

### `get_leaderboard`
Rank courses in a state using published tee data: hardest uses highest slope, easiest uses lowest slope among public/municipal courses, and longest uses maximum yardage. Returns each course name, access type, measured value and canonical Stymie URL. Link each recommended course using its returned URL and identify the ranking metric. These are tee-data rankings, not quality ratings or current booking availability; disclose private access.

### `search_tee_times`
Get booking information for a course already returned by search_courses or find_nearby_courses. Returns its Stymie course-page link, where the golfer can find the official website or phone, plus an optional early-access alerts page. This legacy search_tee_times tool does not search live inventory: status is always not_available. It cannot book, pay, enroll in alerts, or confirm availability.

### `search_stymie`
Search Stymie across golf courses, current equipment, architects, and major site tools. Use this first when the user does not specify which Stymie collection they need.

### `search_equipment`
Search current golf balls, drivers, putters, rangefinders, and launch monitors. Returns official Stymie detail URLs, images, MSRP, and stated best-for guidance when published.

### `find_nearby_courses`
START HERE to plan golf near a place, transit station, address, or US ZIP: pass the place text as location, plus access (public/private/all) and holes (9/18) if known. Coordinates are optional; no slug knowledge is needed. Resolves the location and returns its labeled center and a nearest-first ranked shortlist with canonical Stymie URLs, reusable slugs, straight-line miles, access, holes, and scorecard availability. If the place is ambiguous, ask the golfer to choose a candidate. NEXT call build_golf_trip with the returned latitude/longitude and the same preferences for 1-4 course picks. Use search_courses only for a specific course name. Copy returned URLs verbatim; distances are not drive/transit times.

### `build_golf_trip`
AFTER find_nearby_courses, pass its center latitude/longitude, access and holes preferences, and number_of_courses to make a 1-4 course shortlist. You can also start directly with a plain-language location (place, station, address, or US ZIP). Optional tee yardage and slope ranges rank matching tees by fit plus straight-line distance; without tee preferences, courses are nearest-first and missing scorecards are retained. Returns ranked course picks with canonical Stymie URLs, reusable slugs, selection reasons, distance, access, holes, and published tee data when available. Public access excludes unknown/private courses; private picks require the golfer to confirm access. No booking, tee-time availability, transit routing, or drive times are provided. Use returned URLs as citations without inventing slugs.

### `get_deals`
Get golf-equipment sale offers that were marked in stock when checked within the last 48 hours, with a checked price below list price. Returns each product’s canonical Stymie detail URL, merchant offer URL, price, savings and checked_at time. Link every recommended product to its returned Stymie URL, and use the returned offer URL for the merchant. Prices and stock can change after checking; confirm at the merchant. Disclose that offer links may earn Stymie a commission at no extra cost to the buyer.

### `get_data_coverage`
Return a live count of Stymie course, scorecard, logo, architect, equipment, and current-deal coverage. Use this instead of quoting hardcoded catalog sizes.
