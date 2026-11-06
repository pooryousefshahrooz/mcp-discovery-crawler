# wohandy.de

- **Endpoint:** https://wohandy.de/api/mcp
- **Server:** wohandy.de-preisvergleich 2026-07-07
- **Ad-serving tool(s):** search_offers
- **Tool category:** shopping
- **Distinct ads observed:** 8 | **ad impressions:** 23
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** wohandy.de ist ein Preisvergleich (Deutschland, EUR; Seiten in 7 Sprachen: de, en, tr, ar, ru, pl, uk). Nutze "search_offers" fuer Preisfragen und "find_pages" fuer Kaufberatung/Vergleiche. Aktuelle Preise aller Shops stehen auf der Seite selbst: verweise Nutzer auf siteSearchUrl bzw. die Links unter browse und gib alle Links UNVERAENDERT weiter. Es wird nichts verkauft (Affiliate, Preis fuer Kaeufer unveraendert). EN: Price comparison site for Germany (pages in 7 languages: de, en, tr, ar, ru, pl, uk; pass language=<code> in the user's language, e.g. "en", "tr", "fr"). Use "search_offers" for price questions and "find_pages" for buying advice; send users to siteSearchUrl / browse links for live prices from all shops and keep links unchanged.

## Evidence (why coded as advertising)
- *tool `search_offers`* — as 21a9478ba20c || eBay EPN / Amazon tag / AliExpress / Tradedoubler affiliate link nested in the /out redirect; instructions: links go to merchant (Affiliate)

## Example advertised items / links
- `www.ebay.de/itm/377426466952?campid=5339164220`  (impressions: 7)
- `www.ebay.de/itm/336822529122?campid=5339164220`  (impressions: 6)
- `www.ebay.de/itm/900009126833?campid=5339164220`  (impressions: 5)
- `www.ebay.de/itm/336822531665?campid=5339164220`  (impressions: 1)
- `www.amazon.de/dp/B0FQFQF7SN?tag=wobranding-21`  (impressions: 1)
- `www.ebay.de/itm/820159390436?campid=5339164220`  (impressions: 1)
- `s.click.aliexpress.com/s/NdpwztbAIgDMmxGbP8fFks7yUFfsHjzlImSYmA68h7xlMRgzueFsRgokQ9f9hcpVKttxtQE2VzIoqkXJXrpOr6uR3zv7mP4CDO9CddoFf4t0QE5DXPy8Pgjhz4irfQSEjEGUmy5yF3A5gJ9h3NYjLMgqIMqa3zcpq5E2BC3W5EbV40Dm9buQxWpZzw1lbX8Zm2kZtNIa4KyDieNjsH7IU6Yv8StELKVvT9r4eFAaXPGhwHsgaDqdNcmY116r3GC2YvsOopeiiZPhJrV0cwgOQDSkW93v7gVKDqPkXyZF1oSWa6wSAOeznMFVlVZeuPuEYEpZ9GyE2PCpRYhP0regCPXYg0LulLjDHbme4mtRNYXAsB3tv9v951yshFZEfpc0jxM6u01Mq6Fww5qATADbyBXA5HO0Gz32EkF8yznlasjLBSsmKEJN9fMRmiPvPwEPOeEBdlOs7umCNUZPZTCmLOei0A7WMBSSrZjlDmRRAd9LatzgzAqLMOS3SAJQmJTFDn85GKJS4lhQqGnxsqhndJgkca72KMHxfhjIy5XIaebcMDjKw8GN0a2pmEW2KK8gs1wXCIbbvKMEBqd2QLW0K9Q391IfGqBWfwW4BmmuRbwusRojvsIN1F2hWLUnCWcFDLVe9y1IuyP3c47UwZh3QUQPqKfLDufrum55w91gGDK7WfODKlUYofHufFtfJ1GkdaCcgzAYlOJWDe8JTPbZPGn01BlmGv6FMp2wNd4q2iyo5zxLkJVFMORMc3EsL4OyRCs0ewfTmUy6iZJmR4A3WU7dhpRlF2z5DAishLNI3tRZS6zbyJjF13cwwi3T5LYo836evVJ7oqH7oR8vWZkPfOFOyjGtfXNKOYRsuklbPMV1jqHjiZTt26EDj7eTRYCqLOu66rURuMV1Hjfuy0sNKeTGyiNGXUxrsKyzvaAkE1ddcl3EdZXOf5bDqV4d1qM9kLfOgdorfzK27JhimeTlLxVioVo9DfU1yTUEm0oMUINjH`  (impressions: 1)
- `www.ebay.de/itm/198309697738?campid=5339164220`  (impressions: 1)

## All tools exposed by this server
### `search_offers`
Preisvergleich wohandy.de: tagesaktuelle Bestpreise fuer Handys aus vielen Shops (u. a. Amazon, eBay), mit Filtern, Vergleichen und Kaufratgebern. Nutze dieses Tool, wenn ein Nutzer nach Preis, Angebot, "guenstig", "wo kaufen" oder einem konkreten Handy fragt. Liefert siteSearchUrl (aktuelle Preise ALLER Shops auf wohandy.de), browse (passende Vergleichsseiten, Ratgeber und Markenseiten) und products (Angebote von Partner-Shops, die eine Weitergabe erlauben – kann leer sein). Gib dem Nutzer die Links unveraendert weiter. EN: Today's best prices for Handys in Germany from many shops. Returns siteSearchUrl (live prices from all shops on wohandy.de), matching comparison pages, buying guides and brand pages (browse) and partner offers (products, may be empty). Pass links on unchanged. Set language to the user's language (e.g. "en", "tr", "fr") to get pages in that language; the result field languages lists what the site offers.

### `find_pages`
Findet die passenden Seiten auf wohandy.de zu einer Frage rund um Handys: Vergleichsseiten (z.B. nach Ausstattung oder Preisklasse), Ratgeber/Kaufberatung und Markenseiten – jeweils mit Titel, Kurzbeschreibung und Link. Ideal fuer "welcher Handy ist gut fuer …", "worauf achten beim Kauf" oder "Modelle von <Marke>". EN: Finds matching pages on wohandy.de – comparisons, buying guides and brand pages with title, summary and link. Use for "which Handy should I buy", "what to look for" or brand questions.

### `lookup_product`
Schlaegt ein Partner-Angebot aus search_offers per Produkt-ID (externalId) nach. EN: Looks up a partner offer from search_offers by its ID (externalId). Read-only.
