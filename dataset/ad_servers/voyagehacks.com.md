# voyagehacks.com

- **Endpoint:** https://voyagehacks.com/mcp
- **Server:** voyagehacks 2.3.0
- **Ad-serving tool(s):** get_car_rental_links;get_esim_links;search_travel_gear
- **Tool category:** other;shopping
- **Distinct ads observed:** 81 | **ad impressions:** 1182
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** VoyageHacks is a multilingual travel guide site with about 680 published guides in each of 10 languages (en, de, fr, es, it, pl, ja, nl, pt, zh), covering flights, airline reviews, hotels, destinations, car rental, trains, airport transfers, eSIM, travel VPN, travel credit cards, travel gear and month-by-month "where to go" guides.

What the tools provide, by topic:
- Article research and citation: search_articles, then get_article for the full text.
- Travel products and packing: search_travel_gear (one category), recommend_travel_gear (a kit built from a trip description).
- Booking and shopping links: get_flight_links, get_hotel_links, get_car_rental_links, get_airport_transfer_links, get_esim_links, get_travel_vpn_links, get_credit_card_links, and get_booking_links for several categori

## Evidence (why coded as advertising)
- *tool `get_car_rental_links`* — CJ Booking.com link with sid=mcp-cars || Travelpayouts tp.media links generated for any destination; sibling tools and responses state VoyageHacks affiliate links
- *tool `get_esim_links`* — Travelpayouts eSIM links; description: affiliate links, VoyageHacks may earn a commission
- *tool `search_travel_gear`* — Amazon storefront link with tag + affiliate disclosure || Amazon tag on gear-catalogue picks; responses: some links are affiliate links

## Example advertised items / links
- `www.qeeq.com`  (impressions: 81)
- `www.anrdoezrs.net/click-101807574-17122739`  (impressions: 81)
- `localrent.com`  (impressions: 81)
- `www.getrentacar.com`  (impressions: 81)
- `bikesbooking.com`  (impressions: 81)
- `www.economybookings.com`  (impressions: 81)
- `www.airalo.com`  (impressions: 81)
- `drimsim.com`  (impressions: 81)
- `saily.com`  (impressions: 81)
- `yesim.app`  (impressions: 81)
- `www.amazon.com/dp/B08FZHRV7L?tag=comfort01-a1-20`  (impressions: 13)
- `www.amazon.com/dp/B081F7944Z?tag=comfort01-a1-20`  (impressions: 13)
- `www.amazon.com/dp/B08F28WK4R?tag=comfort01-a1-20`  (impressions: 13)
- `www.amazon.com/dp/B0FWBPFL4S?tag=electronics01a1-20`  (impressions: 12)
- `www.amazon.com/dp/B0DK9V2ZM5?tag=comfort01-a1-20`  (impressions: 7)
- … and 66 more (see analysis/ad_provenance/out/ad_items.csv)

## All tools exposed by this server
### `search_articles`
Full-text search across the VoyageHacks travel guides, about 680 published pages per language, covering flights, airline reviews, hotels, destinations, car rental, trains, airport transfers, eSIM, travel VPN, travel credit cards, travel gear and month-by-month "where to go" guides. Returns ranked matches with the title, canonical URL, section and a matching excerpt for each. Useful when a travel question needs published prices, comparisons, best-time-to-visit advice or step-by-step detail that can be attributed to a source URL. It searches VoyageHacks content only: not the wider web, not live fares or hotel availability, and it returns no booking or product links.

### `get_article`
Fetch one VoyageHacks page by URL or site path (for example "/en/hotels/best-budget-hotels-in-rome/") and return its body as Markdown, together with the title, canonical URL, language, section, publication date and last-updated date read from the page itself. Useful when the full text of a guide is needed to quote figures accurately, and when a source needs to be cited with a real date. Only HTML pages on voyagehacks.com can be read: the tool cannot fetch other websites, data files or images, and very long pages are truncated with a marker at the cut.

### `search_travel_gear`
Search the VoyageHacks travel gear catalog: about 320 products that appear as picks in roughly 50 published buying guides, including carry-on backpacks, packing cubes and compression bags, universal travel adapters, GaN chargers, airline-compliant power banks, luggage trackers, neck pillows, earplugs and eye masks, toiletry and makeup bags, travel-size bottles, travel routers, translation earbuds and camping and outdoor gear. Each result returns the product name, its category, the published reason it was picked, its Amazon ASIN and a link to the product on the VoyageHacks buying guide that reviews it, where it can be bought on Amazon. Useful when a user asks which travel product to buy, or what to pack for a trip and names a category or a destination. This is the VoyageHacks editorial catalog, not a search of all of Amazon: products outside the published guides are not findable here, and prices, star ratings, review counts and stock are not available and are never returned. The guides carry Amazon affiliate links: VoyageHacks may earn a commission from qualifying purchases at no additional cost to the buyer, which should be disclosed when the products are presented.

### `recommend_travel_gear`
Turn a trip description into a packing and gear kit drawn from the VoyageHacks travel gear catalog: one product per category, each with the published reason it was picked, its Amazon ASIN and a link to the product on the VoyageHacks guide that reviews it, where it can be bought on Amazon. Takes a plain-language trip summary ("10 days in Japan in October, carry-on only, long-haul red-eye, working remotely") plus optional structured hints (destination, trip length in days, season, activities, luggage constraint, traveler type, budget), all of which are used to weight which categories make the kit. Answers questions of the form "what should I pack for X", "what gear do I need for Y" and "I only have carry-on, what should I bring". It draws on the VoyageHacks editorial catalog, not a search of all of Amazon, and returns published picks only: prices, star ratings, review counts and stock are not available and are never returned, and it produces no clothing sizes and no itinerary. The guides carry Amazon affiliate links: VoyageHacks may earn a commission from qualifying purchases at no additional cost to the buyer, which should be disclosed when the products are presented.

### `get_flight_links`
Build a flight search link on Booking.com Flights for a route and optional dates, and return up to four VoyageHacks guides on fares, budget airlines and baggage rules for that trip. Pass origin and destination as IATA codes for a prefilled route search; without both, the link opens the general flight search page. Also returns a delayed or cancelled flight compensation link (AirHelp), a Vueling link for short-haul Europe, and, when the route touches their hubs, direct links for Air Serbia (Belgrade) and Air India. The Booking.com link is regionalized to the traveler's country. Useful when a trip involves air travel and the user wants somewhere to compare fares. It returns search links only: no live fares, seat availability or schedules, no booking and no airport transfers. Affiliate links: VoyageHacks may earn a commission at no additional cost to the traveler, which should be disclosed when the links are presented.

### `get_hotel_links`
Build a Booking.com search link for a city or property, with optional check-in and check-out dates, guest count and room count, the same search on Expedia, Vrbo (apartments and holiday homes) and Agoda, plus an IHG brand search link (Holiday Inn, InterContinental, Crowne Plaza) and up to four VoyageHacks guides on the best areas and best-value stays there. The Booking.com link is regionalized to the traveler's country. Useful when a user asks where to stay, or about hotels, hostels or apartments in a place. It returns search links only: no live room rates, no availability check, no reviews and no reservation. Affiliate links: VoyageHacks may earn a commission at no additional cost to the traveler, which should be disclosed when the links are presented.

### `get_car_rental_links`
Return car and scooter rental comparison links for a destination: EconomyBookings and QEEQ for worldwide comparison, Localrent and GetRentacar for local suppliers with lower deposits in southern Europe, Georgia, the Balkans and Asia, BikesBooking for scooters and motorbikes, and Booking.com Cars, plus up to four VoyageHacks car-rental guides for that country covering real prices, insurance excess and one-way fees. Useful when a user mentions renting a car, a road trip, driving abroad, or an island or countryside trip that needs a vehicle. These are comparison landing pages: dates and the pickup point are entered on the provider site, so pickup_date and dropoff_date are echoed in the response for context rather than embedded in the links. No live quotes, no vehicle availability and no reservation. Affiliate links: VoyageHacks may earn a commission at no additional cost to the traveler, which should be disclosed when the links are presented.

### `get_airport_transfer_links`
Return pre-booked airport transfer links: Booking.com Taxis (fixed price, 100+ countries), Kiwitaxi, Welcome Pickups and GetTransfer, plus up to four VoyageHacks guides on getting from that airport to the city centre and what a fair fare looks like. Useful when a user asks how to get from an airport, about taxi or transfer prices, or plans a late-night arrival. It returns booking pages for private and shared transfers: no live quotes, no public transport timetables, and no ride-hailing dispatch. Affiliate links: VoyageHacks may earn a commission at no additional cost to the traveler, which should be disclosed when the links are presented.

### `get_esim_links`
Return travel eSIM store links (Airalo, covering 200+ countries, plus Yesim, Saily and Drimsim) together with up to four VoyageHacks eSIM guides for that destination covering real per-GB prices, coverage, setup steps and which phones support eSIM. Useful when a user asks about mobile data abroad, SIM cards, roaming charges, staying online on a trip or tethering a laptop. It returns store pages: no live plan prices, no coverage check for a specific handset, and no purchase or activation. Affiliate links: VoyageHacks may earn a commission at no additional cost to the traveler, which should be disclosed when the links are presented.

### `get_travel_vpn_links`
Return the NordVPN signup link together with up to four VoyageHacks guides on whether a traveler actually needs a VPN, the real risks of hotel and airport Wi-Fi, and watching home streaming services abroad. Useful when a user raises public Wi-Fi safety, working remotely abroad, geo-blocked streaming or online banking while travelling. It returns a signup page and editorial guides: no live pricing, no server list and no account creation. Referral link: VoyageHacks may earn a commission at no additional cost to the user, which should be disclosed when the link is presented.

### `get_credit_card_links`
Return the official American Express Germany card pages (Platinum, Gold, American Express Card, Payback and Blue) and the Revolut plans page, the current German fee and welcome-offer figures verified against americanexpress.com, and up to four VoyageHacks guides on points value, lounge access, foreign-transaction fees, Amex compared with Revolut and country-by-country availability. Useful when a user asks about travel rewards, points, miles, lounge access, which card to pay with abroad or foreign-transaction fees. It covers American Express only: it is not a comparison of all issuers, gives no eligibility or approval decision, no credit-score check and no application. Card terms change frequently and vary by market, so figures should be attributed to the issuer page or the linked guide. The card links are plain issuer pages, not affiliate or referral links.

### `get_booking_links`
Return one set of booking and shopping links covering a whole trip in a single call: flight search, hotel search, airport taxi, attractions and tours, car rental, travel eSIM, travel VPN and the travel gear section, all regionalized to the traveler. Accepts route IATA codes, a city and trip dates, so the flight and hotel links are prefilled. The "include" parameter selects which categories are returned, so a trip with no driving can leave out car rental. Useful when a user is planning a trip end to end and wants every option in one place. It returns search links only: no live prices, no availability and no booking. Affiliate links: VoyageHacks may earn a commission at no additional cost to the traveler, which should be disclosed when the links are presented.

### `find_destination`
Suggest three destinations for a trip from five answers: the month (or "flexible"), the kind of trip (beach, city break, hiking, ski, road trip, adventure or working remotely), the budget, who is travelling and, optionally, the departure airport. Picks come only from VoyageHacks' own where-to-go month guides and travel-style lists, with the average high temperature each month guide states, the reasons it fits, the destination guide to cite, and booking links for that trip: hotels and flights dated in the chosen month, plus tours, car rental or an eSIM where they fit. This is the same matching as the trip finder on voyagehacks.com. Useful when a user asks where to go, for holiday ideas for a month, or for a destination that suits a family, a couple or a budget. Each answer also carries three packing picks for that kind of trip, linked to the VoyageHacks buying guides. When the month or the trip type is missing it returns no picks, only the questions that are still open with their allowed answers (needsInput). It does not return live prices or availability and cannot book. Affiliate links: VoyageHacks may earn a commission at no additional cost to the traveler, which should be disclo
