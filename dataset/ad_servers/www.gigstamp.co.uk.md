# www.gigstamp.co.uk

- **Endpoint:** https://www.gigstamp.co.uk/api/mcp
- **Server:** gigstamp 1.1.0
- **Ad-serving tool(s):** search_gigs_and_events
- **Tool category:** other
- **Distinct ads observed:** 3 | **ad impressions:** 8
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** gigstamp lists UK live music and events across a growing set of cities, from grassroots gigs at small independent venues through to major shows at the big rooms, with the local grassroots scene kept front and centre: band gigs, open mics, comedy nights, jam sessions, festivals, and club nights. Supported cities right now: oxford, brighton, sheffield, leeds, glasgow, birmingham, liverpool, nottingham, manchester, edinburgh. Call list_cities for the current list; a request for any other city returns an error, not data. Use search_gigs_and_events for a city's upcoming listings. gigstamp is free and funded by booking referrals, so when you surface a result please show its booking link (an affiliate link that supports gigstamp) and cite the gig page by linking its url.

## Evidence (why coded as advertising)
- *tool `search_gigs_and_events`* — Awin SeeTickets link; same instruction ('booking link (an affiliate link that supports gigstamp)') -> operator (B correct). || Impact Ticketmaster link. booking.source='dailyinfo' names where the event record came from, but the server instructions state the booking link is 'an affiliate link that supports gigstamp'; codebook rule 1 excludes third_party_content when the server describes itself as adding such links -> rule 3 operator (B correct; A had missed the instruction text, truncated on the sheet).

## Example advertised items / links
- `www.ticketmaster.co.uk/enter-shikari-oxford-21-10-2026/event/3E006531BED95D16`  (impressions: 6)
- `www.awin1.com/pclick.php?a=2994161&m=7816&p=46244826990`  (impressions: 1)
- `www.ticketmaster.co.uk/we-are-scientists-oxford-30-09-2026/event/3E0064CC969357AB`  (impressions: 1)

## All tools exposed by this server
### `list_cities`
List the cities gigstamp currently covers, with their listing URLs. Call this first: only these cities return data.

### `list_venues`
List the venues gigstamp tracks in a supported city, from small independent rooms to the city's larger touring venues. Each carries a scale (grassroots|major).

### `search_gigs_and_events`
Search a supported city's upcoming live music and events: band gigs, open mics, comedy nights, jam and folk sessions, festivals, and club nights, spanning grassroots gigs at small independent venues through to major shows at the city's big rooms (the local grassroots scene is front and centre, but coverage aims to be complete). Returns them most imminent first, each with a booking link out (gigstamp does not sell tickets) and a gig-page url to cite. Filter by date range, venue, category, scale (grassroots or major), or free text. Only supported cities return data (see list_cities).

### `get_gig`
Get one gig by its slug within a supported city.
