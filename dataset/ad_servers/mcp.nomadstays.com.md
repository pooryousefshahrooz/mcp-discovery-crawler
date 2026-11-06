# mcp.nomadstays.com

- **Endpoint:** https://mcp.nomadstays.com/mcp
- **Server:** nomadstays-mcp-server 0.9.3
- **Ad-serving tool(s):** getMarketplaceAdverts
- **Tool category:** other
- **Distinct ads observed:** 50 | **ad impressions:** 55
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** Nomad Stays: search, check availability and book long-stay accommodation for digital nomads, and let Stay Partners manage their own listings. If you are helping a Stay owner list or set up a new property, read the onboarding briefing first: the 'onboard-new-stay' prompt or the resource guide://onboarding/new-stay. It gives the order of steps, which tools to call, and which steps only the owner can do on the website.

## Evidence (why coded as advertising)
- *tool `getMarketplaceAdverts`* — getMarketplaceAdverts: classified adverts from the operator's marketplace (description: third-party partner deals)

## Example advertised items / links
- `www.nomadstays.com/ad/651`  (impressions: 2)
- `www.nomadstays.com/ad/652`  (impressions: 2)
- `www.nomadstays.com/ad/649`  (impressions: 2)
- `www.nomadstays.com/ad/653`  (impressions: 2)
- `www.nomadstays.com/ad/648`  (impressions: 2)
- `www.nomadstays.com/ad/610`  (impressions: 1)
- `www.nomadstays.com/ad/569`  (impressions: 1)
- `www.nomadstays.com/ad/563`  (impressions: 1)
- `www.nomadstays.com/ad/594`  (impressions: 1)
- `www.nomadstays.com/ad/587`  (impressions: 1)
- `www.nomadstays.com/ad/584`  (impressions: 1)
- `www.nomadstays.com/ad/606`  (impressions: 1)
- `www.nomadstays.com/ad/639`  (impressions: 1)
- `www.nomadstays.com/ad/599`  (impressions: 1)
- `www.nomadstays.com/ad/573`  (impressions: 1)
- … and 35 more (see analysis/ad_provenance/out/ad_items.csv)

## All tools exposed by this server
### `getStayByID`
Returns full details for a single stay. The id parameter searches both EntryId and StayId fields.

### `signupNomadStaysAccount`
Creates a new NomadStays account on behalf of a person who does not have one yet. No authentication required — this is how an AI agent gets a person started. The account is created but inactive until the person clicks the confirmation link sent to their email; this call returns no session or token, so the agent cannot sign in or act as the user itself. Once confirmed, the person can log in at nomadstays.com/Account/Login and request their own MCP bearer token or OAuth grant to let an agent manage their account/listings going forward.

### `getStaysByCountry`
Returns stays from the NomadStays database. Search by 2-letter country code (e.g., 'MA', 'US') or country name (e.g., 'Antigua' matches 'Antigua and Barbuda')

### `getStaysByContinent`
Returns stays from the NomadStays database filtered by continent. Search by continent name (e.g., 'Europe', 'Asia', 'Africa', 'North America', 'South America', 'Oceania')

### `getStaysByLocation`
Returns stays from the NomadStays database that match a location search term. Searches across City, State, location_name, location_country, and location_description fields. Use this for flexible location searches (e.g., 'Paris', 'California', 'Beach', 'Mountain')

### `searchHelpCenter`
Search NomadStays Help Center articles from the public knowledgebase endpoint and return matching title/content/slug entries.

### `getHelpCenterArticle`
Fetch a specific NomadStays Help Center article by its ID. Returns the full article content, title, slug, and categories.

### `listHelpCenterCategories`
List all available NomadStays Help Center categories. Returns category ID, name, slug, description, and article count for each category.

### `getStaysByLifestyle`
Returns stays from the NomadStays database filtered by lifestyle/genre category (e.g., 'Digital Nomad', 'Beach Life', 'City Living', 'Mountain Retreat'). Each stay can belong to multiple lifestyle categories.

### `getStaysByBudget`
Search for stays that fit within a budget for a given duration. Country is OPTIONAL - can search globally or filter by specific country. Perfect for queries like 'Find me somewhere to stay for 1 month under EUR 1000' or 'Find me a place in Spain for 1 month under EUR 1000'.

### `getStaysByAmenities`
Find all stays that have specific amenities. Searches both stay-level amenities (referenced by tbStayFacilities) and room-level amenities (referenced by tbRoomFacilities). Use matchType 'any' to find stays with at least one amenity, or 'all' to find stays with all requested amenities. Can optionally filter by minimum WiFi download speed.

### `getStaysByWiFiSpeed`
Find all stays with WiFi download speed greater than 10Mbps, listed and not suspended.

### `getAllLifestyles`
Returns all active lifestyle/genre categories available in NomadStays. Use this to discover what lifestyle categories exist before searching with getStaysByLifestyle.

### `getStayCountsByCountry`
Returns how many stays NomadStays has in each country, most first. Each row has the country name, 2-letter code, continent, 'stays' (live public listings) and 'bookableNow' (those currently listed for booking). Use this for questions like 'which countries have the most stays', 'how many stays do you have in Spain' or 'where do you have stays'. Optionally filter by continent.

### `getAllAmenities`
List all possible amenities in the database, grouped into Stay Amenities (referenced by tbStaysFacilities) and Room Amenities (referenced by tbStaysRoom.RoomFacilityFk).

### `checkStayAvailability`
Check if a specific stay is available for given check-in and check-out dates. Returns availability status and room details.

### `hasAvailabilityInWindow`
Efficiently checks whether a stay has ANY open booking window of a minimum length within a date range, without checking every single day. Use this to filter search results down to stays with real availability somewhere in the near future (e.g. 'available at all in the next 6 months for a month-long stay'), instead of calling checkStayAvailability repeatedly for individual dates.

### `findNearestAvailability`
Find the nearest available dates when requested dates are not available. Searches for alternative check-in dates within a specified window and can adjust length of stay.

### `getAvailabilityByMonth`
Get all available booking windows in a specific month that meet the minimum length of stay requirement. Returns all possible check-in dates and their corresponding available periods.

### `getRoomAvailability`
Check a specific room's availability for each night in a date range. Returns availability status (available/not available) for each night.

### `getRoomAmenities`
Get comprehensive list of all facilities and amenities for a specific room, including WiFi metrics (download/upload speed, jitter). Returns room details, all facilities, and network performance data.

### `getMyStays`
List all Stays owned by the account bound to the MCP agent token. Returns stayId, title, and listed status for each — use this to find a stayId before calling any other owner-scoped tool. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getMyStayDetail`
Get the current title, description, and listed status for one of your Stays. Call this before updateStayDetail so the agent knows the current values and doesn't accidentally overwrite them. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getMyStayOnboardingStatus`
Get the Stay's listing-completion scores — the same six 'Listing Completion' cards shown on the Stay dashboard (Stay Details, Availability, Rooms, Packages, Wi-Fi, Operator Information), plus an overall completion percentage. Use this when a host asks how far along they are with onboarding or what's left to finish. Note: Wi-Fi is a test-freshness score (recency of the last speed test), not a speed rating. Operator Information is the same score the owner's dashboard shows, with a missingItems list of labels (e.g. 'Date of Birth', 'Banking Details') — those fields are owner-only and never writable via MCP, so relay the list to the owner. Stay Details is recalculated automatically after every MCP edit to details, organisational data, contacts, facilities or photos. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getMyStayRooms`
List all rooms currently configured on one of your Stays, including bed setup, occupancy, facilities (resolved to names, not just IDs), and every room/workspace photo as a viewable CDN URL. Call this before createStayRoom, updateStayRoom, deleteStayRoom, deleteRoomPhoto, or reorderRoomPhotos so the agent can show current values or find the right roomId/fileName. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getMyStayPackages`
List all pricing packages on one of your Stays, including their full price tiers (days, buy price, sell price, comparison price, listed status). Call this before createStayPackage or updateStayPackage — hosts often forget exactly what packages/pricing they've already set. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getMyStayOrganisationalData`
Get a Stay's organisational data: address, check-in/out policy, pets/children/parking, cancellation policy, tourism/land-registration numbers. Call this before updateStayOrganisationalData so the agent knows current values. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getMyBusinessProfile`
Get the host account's business profile: legal business name, VAT/business registration numbers, whether registered as a business entity. Does NOT include bank or tax-ID details — those are never exposed via MCP. Call this before updateHostBusinessProfile. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `updateStayDetail`
Update a Stay's title and/or description. Requires an MCP agent token (NOMADSTAYS_MCP_AGENT_TOKEN) scoped to the owning account. Only fields supplied are changed.

### `createStayRoom`
Create a new room on a Stay. Call getRoomTypeOptions(stayId) and getRoomFacilityOptions() first to find valid roomTypeFK/roomFacilityFk values. Boutique Stays are capped at 6 rooms total (one per Boutique1-6 slot) — creation is rejected once all 6 exist. Requires an MCP agent token scoped to the owning account.

### `updateStayRoom`
Update an existing room on a Stay. Only fields supplied are changed. Call getRoomTypeOptions(stayId) and getRoomFacilityOptions() first to find valid roomTypeFK/roomFacilityFk values. Requires an MCP agent token scoped to the owning account.

### `deleteStayRoom`
Delete (soft-delete) a room from a Stay. Requires an MCP agent token scoped to the owning account.

### `getRoomTypeOptions`
List valid room types for a specific Stay's rooms (roomTypeFK in createStayRoom/updateStayRoom). Valid values depend on the Stay: boutique Stays choose from a fixed boutique type range; standard Stays are restricted to types already used on one of their own rooms. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getRoomFacilityOptions`
List every room-level amenity/facility option available (roomFacilityFk in createStayRoom/updateStayRoom) — e.g. Wi-Fi, Air Conditioning, Private Bathroom. Wi-Fi is mandatory and always included even if not explicitly selected. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `deleteRoomPhoto`
Delete one photo from a room's gallery. Call getMyStayRooms first to find the exact fileName. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `reorderRoomPhotos`
Change the display order of a room's photo gallery. fileNames must be the FULL current gallery (same set, just reordered) — call getMyStayRooms first. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `createStayPackage`
Create a new pricing package on a Stay, optionally with initial price tiers. Requires an MCP agent token scoped to the owning account.

### `updateStayPackage`
Update an existing pricing package on a Stay. Supplying 'prices' replaces ALL price rows for that package. Requires an MCP agent token scoped to the owning account.

### `deleteStayPackage`
Permanently delete a pricing package and all its price tiers from a Stay. This is a hard delete (unlike room deletion, which is soft). Requires an MCP agent token scoped to the owning account.

### `getCurrencyOptions`
List valid currency ids/codes for use as a package's currencyFK.

### `updateStayOrganisationalData`
Update a Stay's organisational data: address, check-in/out policy, pets/children/parking, cancellation policy, accommodation type, tourism/land-registration numbers, 'Why Choose Us' reasons, and more. Only fields supplied are changed. IMPORTANT: countryId, petsAllowedId, childrenAllowedId, parkingId, cxPolicyId, and stayTypeId are lookup IDs, NOT plain text or booleans — call getCountryOptions / getAdditionalInformationOptions / getCancellationPolicyOptions / getStayTypeOptions first to find the correct ID to send. Requires an MCP agent token scoped to the owning account.

### `updateHostBusinessProfile`
Update the host account's business profile (legal business name, VAT/business registration numbers). Applies to the account owning the MCP agent token, not a specific stay. Only fields supplied are changed. Does NOT touch bank or tax-ID details — those are not MCP-writable.

### `uploadStayPhoto`
Upload a photo to one of your Stay's photo areas. Supply EXACTLY ONE of 'url' (a public https:// link, e.g. a Google Drive or Dropbox share link — the server downloads it) or 'base64' (the raw image bytes, base64-encoded — use this when you already have the image data in hand, e.g. a user attached a photo in the conversation, and have nowhere public to host it first). The photo is validated against the same minimum specs as a manual upload: JPEG, PNG, or WebP, under 20MB, and a minimum resolution that depends on area. Most areas require at least 1920x1080 landscape; 'host' requires at least 1080x1350 PORTRAIT — a landscape photo will be rejected for that area. Every upload is downscaled to fit within 2560x1440 and re-encoded server-side as WebP (stripping metadata and anything that isn't genuine image data) before storage. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getMyStayContacts`
Get a Stay's contact/owner/manager details and social media links: owner name/email/mobile, manager (day-to-day contact person) name/email/mobile, booking email/phone/mobile, host display name, and website/Facebook/Twitter/YouTube/Instagram/TikTok/LinkedIn links. Call this before updateStayContacts so the agent knows current values. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `updateStayContacts`
Update a Stay's contact/owner/manager details and social media links. Only fields supplied are changed. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getMyStayFacilities`
Get the available options AND current selections for one facility/checkbox group on a Stay — e.g. 'Languages Spoken' returns every language the platform supports plus which ones are currently selected for this Stay. Call getFacilityGroups first if you don't know the exact group name. Common groups: 'General', 'Services', 'Languages Spoken', 'Meal', 'Position', 'Remote Worker'. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `updateStayFacilities`
Set which options are selected for one facility/checkbox group on a Stay — e.g. which languages are spoken. facilityDetailIds is the COMPLETE replacement list: anything not included will be UNCHECKED. Call getMyStayFacilities first to see current selections and valid IDs before changing them. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getFacilityGroups`
List every facility/checkbox group name that exists on the platform (e.g. 'Languages Spoken', 'General', 'Services', 'Meal', 'Position', 'Remote Worker'). Call this first if you don't already know the exact group name to pass to getMyStayFacilities/updateStayFacilities. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getStayTypeOptions`
List valid values for a Stay's 'Main Accommodation Type' (stayTypeId in updateStayOrganisationalData). Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getCountryOptions`
List valid values for a Stay's country (countryId in updateStayOrganisationalData), with each country's name and 2-letter code. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getCancellationPolicyOptions`
List valid values for a Stay's cancellation policy (cxPolicyId in updateStayOrganisationalData). Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getAdditionalInformationOptions`
List valid values for one of the Additional Information picklists used in updateStayOrganisationalData: Children Allowed, Pets Allowed, or Parking. These are NOT booleans — they're lookup IDs (e.g. 'Yes', 'No', 'On Request') — call this to find the right value before writing petsAllowedId/childrenAllowedId/parkingId. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getBusinessModelOptions`
List valid values for a Stay's listing/business model (businessModelId, read-only — displayed on the Stay but not editable via MCP or the host UI itself). Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getMyStayPhotos`
Get every current photo for a Stay across all areas (listing gallery, main/hero, workspace/coworking gallery, host), each as a full https:// CDN URL an agent can view directly (not just a filename). Call this before deleteStayPhoto or reorderStayPhotos to see current filenames. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `deleteStayPhoto`
Delete one photo from a Stay. Call getMyStayPhotos first to find the exact fileName. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `reorderStayPhotos`
Change the display order of a Stay's listing or workspace photo gallery. fileNames must be the FULL current gallery (same set of files, just reordered) — call getMyStayPhotos first. This only reorders; it cannot add or remove photos. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getProductInfo`
Look up a Nomad Stays product's price and purchasability — currently only product 8, the Stay Application fee (EUR 39). Returns isWaivedForCaller: true if the caller is already a Stay Partner re-applying, in which case there's nothing to pay and purchaseProduct will process the waiver automatically. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `purchaseProduct`
Start a purchase of a Nomad Stays product on the caller's own behalf. If the caller already qualifies for a waiver (e.g. an existing Stay Partner re-applying), this resolves immediately with no payment step and returns status 'waived'. Otherwise it returns a checkoutUrl hosted on nomadstays.com — you must hand this URL to the member and ask them to open it in their own browser and pay; you cannot complete payment on their behalf. Poll getPurchaseStatus with the returned saleId afterwards to find out when it's actually paid. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getPurchaseStatus`
Check whether a purchase has been paid. Only ever reports 'paid' after a fresh server-side check against the payment provider — never trust the member's own claim that they've paid, always poll this instead. Possible statuses: pending, paid, failed, waived. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `listStayApplications`
List the caller's Stay Applications (draft and submitted), each with a nextAction hint telling you what's needed next (provide_applicant_details, provide_property_details, pay_application_fee, submit, awaiting_review, or accepted). Call this to find an in-progress application's applicationId before resuming it. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getStayApplication`
Get the full current state of one Stay Application, including a nextAction hint and (if incomplete) a missingFields list naming exactly which required fields are still empty. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `createStayApplication`
Start a new Stay Application for the caller. Any fields can be supplied now or filled in later via saveStayApplication — the applicant's name defaults from their Nomad Stays profile if not supplied. Call getCountryOptions and getBusinessModelOptions first to resolve stayCountryId/postalCountryId/businessModelId, since country-specific rules (VAT number, tourism number, permitted business models) are enforced server-side and rejections name the specific field/reason. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `saveStayApplication`
Update any subset of fields on an existing, not-yet-submitted Stay Application. Same field set and validation rules as createStayApplication — only pass the fields you're changing. Fails with a 409 if the application has already been submitted. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `submitStayApplication`
Submit a completed Stay Application for human review. Rejects with a missingFields list if any required field is still empty, or a 409 if the Application Fee hasn't been paid/waived yet (call purchaseProduct with productId 8 and applicationId first). There is no partial/optimistic submission — everything required must already be in place. On success the application moves to human review; nothing further is needed from the agent. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `listExperienceApplications`
List the caller's Experience Applications (draft and submitted), each with a nextAction hint telling you what's needed next (provide_applicant_details, provide_experience_details, pay_application_fee, submit, awaiting_review, or accepted). Call this to find an in-progress application's applicationId before resuming it. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getExperienceApplication`
Get the full current state of one Experience Application, including a nextAction hint and (if incomplete) a missingFields list naming exactly which required fields are still empty. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `createExperienceApplication`
Start a new Experience Application for the caller. Any fields can be supplied now or filled in later via saveExperienceApplication — the applicant's name defaults from their Nomad Stays profile if not supplied. Call getCountryOptions and getBusinessModelOptions first to resolve experienceCountryId/postalCountryId/businessModelId, since country-specific rules (VAT number, tourism number, permitted business models) are enforced server-side and rejections name the specific field/reason. Experiences must run a minimum of 4 days. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `saveExperienceApplication`
Update any subset of fields on an existing, not-yet-submitted Experience Application. Same field set and validation rules as createExperienceApplication — only pass the fields you're changing. Fails with a 409 if the application has already been submitted. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `submitExperienceApplication`
Submit a completed Experience Application for human review. Rejects with a missingFields list if any required field is still empty, or a 409 if the Application Fee hasn't been paid/waived yet (call purchaseProduct with productId 9 and applicationId first — Experience uses product 9, NOT product 8). There is no partial/optimistic submission. On success the application moves to human review. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `quoteStayBooking`
Get a server-computed price and availability quote for booking a Stay package on the caller's own behalf. Price is always re-derived from the package's actual pricing tiers — never trust or reuse a price shown elsewhere. Picks the largest price tier whose length is <= the requested nights (e.g. 10 nights against 7/14/21/30-day tiers uses the 7-day tier's rate), falling back to the smallest tier if the stay is shorter than all of them. Returns a quoteId valid for about 15 minutes — call bookStay with it to actually create the booking and get a payment link. Requires the caller's token to carry the 'bookings' OAuth scope (McpMember role), separate from the listings-management 'McpAgent' scope other tools here use.

### `bookStay`
Create a real booking from a quoteId returned by quoteStayBooking, and return a hosted checkoutUrl. The quote's price/availability is re-validated server-side one more time before the booking is created — a stale or expired quote will be rejected with a message to call quoteStayBooking again. You MUST send the checkoutUrl to the member and tell them to open it in their own browser to pay — you cannot complete this payment on their behalf, and no card details ever pass through you. Requires NOMADSTAYS_MCP_AGENT_TOKEN with the 'bookings' scope.

### `createStayEnquiry`
Send an enquiry about a Stay that can't be booked right now — for example quoteStayBooking finds no bookable package, or the Stay page says it isn't bookable online. The enquiry goes to the Nomad Stays team, who check availability with the Stay and reply to the member by email (usually within one working day). The member's name and email come from their Nomad Stays account; do not ask for them. Only send an enquiry the member has asked for, and include what they told you (who is travelling, work needs, questions). Use bookStay instead whenever a quote succeeds. Requires the 'bookings' scope.

### `getBookingStatus`
Check a Stay booking's real payment status by PNR. Status is always freshly re-verified against Airwallex directly if not already confirmed paid — never trust a client-supplied claim of success. Only ever returns bookings owned by the caller's own account. Requires NOMADSTAYS_MCP_AGENT_TOKEN with the 'bookings' scope.

### `listMyBookings`
List all Stay bookings owned by the caller's own account, most recent first, with each one's current status. Each booking includes needsAction: true if it's still unpaid, with a ready-to-use checkoutUrl — call this proactively (e.g. at the start of a session, or when the member asks what's pending) and surface any needsAction bookings to the member, since there is no other way for them to be notified of an incomplete booking through this connection. Requires NOMADSTAYS_MCP_AGENT_TOKEN with the 'bookings' scope.

### `listCoworkingApplications`
List the caller's Coworking Applications (draft and submitted), each with a nextAction hint (provide_coworking_details, submit, awaiting_review, or accepted). Coworking has no Application Fee, so unlike Stay/Experience there is no pay_application_fee step. Call this to find an in-progress application's applicationId before resuming it. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `getCoworkingApplication`
Get the full current state of one Coworking Application, including a nextAction hint and (if incomplete) a missingFields list naming exactly which required fields are still empty. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `createCoworkingApplication`
Start a new Coworking Application for the caller. Much simpler than the Stay/Experience applications: no VAT/tourism-number/business-model rules, no Application Fee, and no billing step at all — once coworkingName, applicantName, applicantEmail, city and country are present, nextAction goes straight to 'submit'. Call getCountryOptions first to find a valid country name (must be the exact tbCountry.CountryName, not an ID). Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `saveCoworkingApplication`
Update any subset of fields on an existing, not-yet-submitted Coworking Application. Same field set and validation rules as createCoworkingApplication — only pass the fields you're changing. Fails with a 409 if the application has already been submitted. Requires NOMADSTAYS_MCP_AGENT_TOKEN.

### `submitCoworkingApplication`
Submit a completed Coworking Application for human review. Rejects with a missingFields list if any required field is still empty. There is no Application Fee to pay for Coworking, so — unlike submitStayApplication/submitExperienceApplication — this never returns a pay_application_fee/409-unpaid response. On success the application moves to human review. Requires NOMADSTAYS_MCP_AGENT_TOKEN.
