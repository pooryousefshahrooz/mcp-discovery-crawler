# woroller.de

- **Endpoint:** https://woroller.de/api/mcp
- **Server:** woroller.de-preisvergleich 2026-07-07
- **Ad-serving tool(s):** search_offers
- **Tool category:** shopping
- **Distinct ads observed:** 5 | **ad impressions:** 15
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** woroller.de ist ein Preisvergleich (Deutschland, EUR; Seiten in 7 Sprachen: de, en, tr, ar, ru, pl, uk). Nutze "search_offers" fuer Preisfragen und "find_pages" fuer Kaufberatung/Vergleiche. Aktuelle Preise aller Shops stehen auf der Seite selbst: verweise Nutzer auf siteSearchUrl bzw. die Links unter browse und gib alle Links UNVERAENDERT weiter. Es wird nichts verkauft (Affiliate, Preis fuer Kaeufer unveraendert). EN: Price comparison site for Germany (pages in 7 languages: de, en, tr, ar, ru, pl, uk; pass language=<code> in the user's language, e.g. "en", "tr", "fr"). Use "search_offers" for price questions and "find_pages" for buying advice; send users to siteSearchUrl / browse links for live prices from all shops and keep links unchanged.

## Evidence (why coded as advertising)
- *tool `search_offers`* — as 21a9478ba20c || eBay EPN / Amazon tag / AliExpress / Tradedoubler affiliate link nested in the /out redirect; instructions: links go to merchant (Affiliate)

## Example advertised items / links
- `www.amazon.de/dp/B0DFM68R9N?tag=wobranding-21`  (impressions: 7)
- `www.amazon.de/dp/B0DHL8S3FF?tag=wobranding-21`  (impressions: 5)
- `www.ebay.de/itm/137645571329?campid=5339164220`  (impressions: 1)
- `www.ebay.de/itm/147592652727?campid=5339164220`  (impressions: 1)
- `www.ebay.de/itm/327328728076?campid=5339164220`  (impressions: 1)

## All tools exposed by this server
### `search_offers`
Preisvergleich woroller.de: tagesaktuelle Bestpreise fuer E-Roller aus vielen Shops (u. a. Amazon, eBay), mit Filtern, Vergleichen und Kaufratgebern. Nutze dieses Tool, wenn ein Nutzer nach Preis, Angebot, "guenstig", "wo kaufen" oder einem konkreten E-Roller fragt. Liefert siteSearchUrl (aktuelle Preise ALLER Shops auf woroller.de), browse (passende Vergleichsseiten, Ratgeber und Markenseiten) und products (Angebote von Partner-Shops, die eine Weitergabe erlauben – kann leer sein). Gib dem Nutzer die Links unveraendert weiter. EN: Today's best prices for E-Roller in Germany from many shops. Returns siteSearchUrl (live prices from all shops on woroller.de), matching comparison pages, buying guides and brand pages (browse) and partner offers (products, may be empty). Pass links on unchanged. Set language to the user's language (e.g. "en", "tr", "fr") to get pages in that language; the result field languages lists what the site offers.

### `find_pages`
Findet die passenden Seiten auf woroller.de zu einer Frage rund um E-Roller: Vergleichsseiten (z.B. nach Ausstattung oder Preisklasse), Ratgeber/Kaufberatung und Markenseiten – jeweils mit Titel, Kurzbeschreibung und Link. Ideal fuer "welcher E-Roller ist gut fuer …", "worauf achten beim Kauf" oder "Modelle von <Marke>". EN: Finds matching pages on woroller.de – comparisons, buying guides and brand pages with title, summary and link. Use for "which E-Roller should I buy", "what to look for" or brand questions.

### `lookup_product`
Schlaegt ein Partner-Angebot aus search_offers per Produkt-ID (externalId) nach. EN: Looks up a partner offer from search_offers by its ID (externalId). Read-only.
