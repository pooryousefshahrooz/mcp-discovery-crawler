# wopool.de

- **Endpoint:** https://wopool.de/api/mcp
- **Server:** wopool.de-preisvergleich 2026-07-07
- **Ad-serving tool(s):** search_offers
- **Tool category:** shopping
- **Distinct ads observed:** 13 | **ad impressions:** 38
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** wopool.de ist ein Preisvergleich (Deutschland, EUR; Seiten in 7 Sprachen: de, en, tr, ar, ru, pl, uk). Nutze "search_offers" fuer Preisfragen und "find_pages" fuer Kaufberatung/Vergleiche. Aktuelle Preise aller Shops stehen auf der Seite selbst: verweise Nutzer auf siteSearchUrl bzw. die Links unter browse und gib alle Links UNVERAENDERT weiter. Es wird nichts verkauft (Affiliate, Preis fuer Kaeufer unveraendert). EN: Price comparison site for Germany (pages in 7 languages: de, en, tr, ar, ru, pl, uk; pass language=<code> in the user's language, e.g. "en", "tr", "fr"). Use "search_offers" for price questions and "find_pages" for buying advice; send users to siteSearchUrl / browse links for live prices from all shops and keep links unchanged.

## Evidence (why coded as advertising)
- *tool `search_offers`* — as 21a9478ba20c || eBay EPN / Amazon tag / AliExpress / Tradedoubler affiliate link nested in the /out redirect; instructions: links go to merchant (Affiliate)

## Example advertised items / links
- `www.ebay.de/itm/307136751176?campid=5339164220`  (impressions: 7)
- `www.ebay.de/itm/206242214764?campid=5339164220`  (impressions: 7)
- `www.ebay.de/itm/840020570543?campid=5339164220`  (impressions: 5)
- `www.ebay.de/itm/800636403962?campid=5339164220`  (impressions: 5)
- `www.ebay.de/itm/397849492450?campid=5339164220`  (impressions: 5)
- `www.ebay.de/itm/167866926913?campid=5339164220`  (impressions: 2)
- `www.ebay.de/itm/840000464057?campid=5339164220`  (impressions: 1)
- `www.ebay.de/itm/840000463580?campid=5339164220`  (impressions: 1)
- `www.ebay.de/itm/158108827800?campid=5339164220`  (impressions: 1)
- `www.ebay.de/itm/168509692725?campid=5339164220`  (impressions: 1)
- `www.amazon.de/dp/B01N3V9YCB?tag=wobranding-21`  (impressions: 1)
- `s.click.aliexpress.com/s/pyFri10M6ltAv61YZY9TfrxiDaaFXRreuZWJMeLtD8jig1wPxn51K2eq59ds8iT5Wl5L3w5KJyrl7SjOO3B0oJ0Xjwnc7n8AQA7gf5qnT4sCyU05LNms9JvyWQNFHNKtzBcoBpSguMg3UBR1FOODkmGTloXosMhqhnKgzzuJPYPxewVvzupiAiKSJA5SK0iQRxmaQ7UPG0AP2HC7uLitVpvXIfjMl7RnsnN7B8FrGfP9TWP7emQeaXV90Bp9fLEiLeKHsRf9R2jgKD32Axm5na4bRJdkhGVyv3GcDgMjmYrrZWinWctR9gnPwA4kJMzBaavEQF9l7wWevytlTQbkI7dMgYOQyXMWNwwMTe8ruQ256sjBqIjZO3EOcBQaapzWd8cK7fX8hwT36GR4LxMTyD4sc1X4IyhVGuDgHULh5ztOsI9tj3uBvhg2lq6cJCM9TWhLdcTXDBENKCfbE19Ol8Da5lL3rv8jObGEveOotc7m9k5fHHlNZegnUTq5gC93CHt1tk9cYoxXzlCSz7uc6jwZi7npsaDPZatV2V2DJ1iPCn5T5NQbxMnrGLDTCXOVU9CQaJjsVYV3MrpOqban0t94ltU4lmvbRmOulOu2jd47f7FTjsaKGRH5EZv248sqGmFByTuWxIPvKWJukM8QTWvRApEliRA5fnaHshI7GpvD2AMs0gofiyMFC0fCpujVEfltRsxMqeoiHwFmlv1cTYObXTGDAXP9uvLSzwvuaLddQEcP27gV836GvK0zaJfrMTOxM4PajtkxTH51DJd9eRro0uM8hK7CGakaBLTRvGlHioN9fxrt1E3nkDYl9KDmFAcnTQhCNMdnQMOXx7V0czhzRa9L7V7sa3ADHl21W7XDSQbPyU2nIFVNEXltMeTOmdDImvwwFLS9h0LpEaOgC0biEqiHGDW3Yw73IAIaNE0i2RlDS4KMRju1q6Q8ewwntX4bbbflNIEgpX15hbM5arWO8K8xGdBevtDYd29ruOVZPuTai4HcXk46lXlMLfxD4K66uo3W`  (impressions: 1)
- `s.click.aliexpress.com/s/pyFri10M6ltAv61YZY9TfrxiDaaFXRreuZWJMeLtD8jig1wPxn51K2eq59ds8iT5Wl5L3w5KJyrl7SjOO3B0oJ0Xjwnc7n8AQA7gf5qnT4sCyU05LNms9JvyWQNFHNKtzBcoBpSguMg3UBR1FOODkmGTloXosMhqhnKgzzuJPYPxewVvzupiAiKSJA5SK0iQRxmaQ7UPG0AP2HC7uLitVpvXIfjMl7RnsnN7B8FrGfP9TWP7emQeaXV90Bp9fLEiLeKHsRf9R2jgKD32Axm5na4bRJdkhGVyv3GcDgMjmYrrZWinWctR9gnPwA4m7YgfcrBXWm719ucINXNgW4GBA8PtHRpm6tqp0O3CZqmOCchkwYsfoLVTYQM6Ltyiu5WbZ0jiLVWCra0kKh95nu3JIcnq9svJKHaEBYXq50hDmRKS0RPHEnZsMZS5JaoGAHkEkpQlERjYi2llox89zPhwxZ1lHIMlIlcRVrn0G1FqHMcg2H364LxWIPNKCHOJVdGXU5dHZdYuoQydcLlmTcgDwAans3Abb11zBMEgNoTaMy3v9zkDC9Hyn0IIo1cf9UNZWgXK7AxatvxXPk8FfZgeATYPhLGBbaWOsSvbQkqXpBn051EfxYqPQRiT8iL5kgh0EbP8jqbBOOFfw7ayRunG25cwmrrFZ3tJM3AcYJj9J4JmTFIZNiaMbxL51dL5t7CbGjML1ay9Af9dmkWVfmOnM8GlRARVpWClHGpt106LQUJPlaIr6j1ef0KMnBEVe0Cxq95bfPg4hTsyaEB5wBQAqN10tEJ1hbSd73mCeoq6oOi9tWybrGNe1kI8SQkDM82dgGKBGsXJyWcXEfNTRTeOWbBe7IRALrffMq0pa6yPX4qPj1neppstaxUifqZFVjQeipn1P39zXulxu451dO7fRyq5yDN2RtmWEDhADtd3KxzLuhPUqbQcHihnn5oSIJxrzGUtoSncGcVRTxdELNaIp5MuBH4a89gCQVdOeXaHEg5sXliizqhBKdj3Bw1neRwrgsu0N2Yy`  (impressions: 1)

## All tools exposed by this server
### `search_offers`
Preisvergleich wopool.de: tagesaktuelle Bestpreise fuer Pools aus vielen Shops (u. a. Amazon, eBay), mit Filtern, Vergleichen und Kaufratgebern. Nutze dieses Tool, wenn ein Nutzer nach Preis, Angebot, "guenstig", "wo kaufen" oder einem konkreten Pool fragt. Liefert siteSearchUrl (aktuelle Preise ALLER Shops auf wopool.de), browse (passende Vergleichsseiten, Ratgeber und Markenseiten) und products (Angebote von Partner-Shops, die eine Weitergabe erlauben – kann leer sein). Gib dem Nutzer die Links unveraendert weiter. EN: Today's best prices for Pools in Germany from many shops. Returns siteSearchUrl (live prices from all shops on wopool.de), matching comparison pages, buying guides and brand pages (browse) and partner offers (products, may be empty). Pass links on unchanged. Set language to the user's language (e.g. "en", "tr", "fr") to get pages in that language; the result field languages lists what the site offers.

### `find_pages`
Findet die passenden Seiten auf wopool.de zu einer Frage rund um Pools: Vergleichsseiten (z.B. nach Ausstattung oder Preisklasse), Ratgeber/Kaufberatung und Markenseiten – jeweils mit Titel, Kurzbeschreibung und Link. Ideal fuer "welcher Pool ist gut fuer …", "worauf achten beim Kauf" oder "Modelle von <Marke>". EN: Finds matching pages on wopool.de – comparisons, buying guides and brand pages with title, summary and link. Use for "which Pool should I buy", "what to look for" or brand questions.

### `lookup_product`
Schlaegt ein Partner-Angebot aus search_offers per Produkt-ID (externalId) nach. EN: Looks up a partner offer from search_offers by its ID (externalId). Read-only.
