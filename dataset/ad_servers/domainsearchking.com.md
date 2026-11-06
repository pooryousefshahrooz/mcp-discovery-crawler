# domainsearchking.com

- **Endpoint:** https://domainsearchking.com/api/mcp
- **Server:** domain-search-king 1.0.0
- **Ad-serving tool(s):** find_available_domains_by_pattern
- **Tool category:** other
- **Distinct ads observed:** 60 | **ad impressions:** 150
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** Three tools: find_available_domains (AI-brandable available .coms for a business idea), find_available_domains_by_pattern (exhaustively list EVERY available domain starts/ends/contains a keyword across .com + .net — the thing other domain tools can't do), and check_domain (full due-diligence report: RDAP registration, backlinks/authority, toxic linkers, Wayback history, trademark links). Availability tools return only verified-available domains. Free up to 10 calls/day (unlimited + a private premium expired-domain catalog at domainsearchking.com).

## Evidence (why coded as advertising)
- *tool `find_available_domains_by_pattern`* — /go registration links; response: 'go through Domain Search King's Namecheap and Spaceship affiliate links' || same registration links, response disclosure

## Example advertised items / links
- `domainsearchking.com/go/womensrunningshoesco.com`  (impressions: 4)
- `domainsearchking.com/go/spaceship/womensrunningshoesio.com`  (impressions: 4)
- `domainsearchking.com/go/womensrunningshoesio.net`  (impressions: 4)
- `domainsearchking.com/go/womensrunningshoesio.com`  (impressions: 4)
- `domainsearchking.com/go/spaceship/womensrunningshoes.net`  (impressions: 4)
- `domainsearchking.com/go/spaceship/womensrunningshoesco.com`  (impressions: 4)
- `domainsearchking.com/go/spaceship/womensrunningshoesco.net`  (impressions: 4)
- `domainsearchking.com/go/womensrunningshoes.net`  (impressions: 4)
- `domainsearchking.com/go/spaceship/womensrunningshoesio.net`  (impressions: 4)
- `domainsearchking.com/go/womensrunningshoesco.net`  (impressions: 4)
- `domainsearchking.com/go/spaceship/wirelessbluetoothheadphones.net`  (impressions: 4)
- `domainsearchking.com/go/spaceship/wirelessbluetoothheadphonesco.com`  (impressions: 4)
- `domainsearchking.com/go/wirelessbluetoothheadphonesio.net`  (impressions: 4)
- `domainsearchking.com/go/wirelessbluetoothheadphonesio.com`  (impressions: 4)
- `domainsearchking.com/go/spaceship/wirelessbluetoothheadphonesco.net`  (impressions: 4)
- … and 45 more (see analysis/ad_provenance/out/ad_items.csv)

## All tools exposed by this server
### `find_available_domains`
Generate brandable .com domain names for a business idea and return ONLY the ones that are currently AVAILABLE to register (checked against the Verisign RDAP registry through a caching proxy; an available answer can be up to 10 minutes old). Give a keyword and, ideally, a short description of the business for better names.

### `find_available_domains_by_pattern`
Exhaustively enumerate EVERY available domain matching a keyword PATTERN, across TLDs — the thing most domain tools/MCPs can't do. Give a keyword (or several) and a position: 'starts' (keyword+word, e.g. Bearoak), 'ends' (word+keyword, e.g. Oakbear), 'contains' (keyword inside a longer invented word, e.g. Oakbearen), or 'all'. Every candidate is checked against the registry (cached answers up to 10 minutes old); only AVAILABLE domains are returned, grouped by TLD. Checks .com and .net by default.

### `check_domain`
Full due-diligence report for one domain: registration age/expiry/status (live RDAP), backlinks & authority from our own Common Crawl link graph, toxic-linker audit, website history (Wayback), trademark search links, and optional blacklist when configured. Use before buying a domain. No composite appraisal score — flags + per-section detail only.
