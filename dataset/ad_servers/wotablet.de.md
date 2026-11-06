# wotablet.de

- **Endpoint:** https://wotablet.de/api/mcp
- **Server:** wotablet.de-preisvergleich 2026-07-07
- **Ad-serving tool(s):** search_offers
- **Tool category:** shopping
- **Distinct ads observed:** 9 | **ad impressions:** 32
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** wotablet.de ist ein Preisvergleich (Deutschland, EUR; Seiten in 7 Sprachen: de, en, tr, ar, ru, pl, uk). Nutze "search_offers" fuer Preisfragen und "find_pages" fuer Kaufberatung/Vergleiche. Aktuelle Preise aller Shops stehen auf der Seite selbst: verweise Nutzer auf siteSearchUrl bzw. die Links unter browse und gib alle Links UNVERAENDERT weiter. Es wird nichts verkauft (Affiliate, Preis fuer Kaeufer unveraendert). EN: Price comparison site for Germany (pages in 7 languages: de, en, tr, ar, ru, pl, uk; pass language=<code> in the user's language, e.g. "en", "tr", "fr"). Use "search_offers" for price questions and "find_pages" for buying advice; send users to siteSearchUrl / browse links for live prices from all shops and keep links unchanged.

## Evidence (why coded as advertising)
- *tool `search_offers`* — as 21a9478ba20c || eBay EPN / Amazon tag / AliExpress / Tradedoubler affiliate link nested in the /out redirect; instructions: links go to merchant (Affiliate)

## Example advertised items / links
- `www.amazon.de/dp/B0G119PFVV?tag=wobranding-21`  (impressions: 7)
- `www.ebay.de/itm/800640285595?campid=5339164220`  (impressions: 6)
- `www.ebay.de/itm/356639206928?campid=5339164220`  (impressions: 5)
- `www.ebay.de/itm/168505385337?campid=5339164220`  (impressions: 5)
- `www.ebay.de/itm/168515574276?campid=5339164220`  (impressions: 5)
- `www.ebay.de/itm/800640275995?campid=5339164220`  (impressions: 1)
- `www.ebay.de/itm/168515590083?campid=5339164220`  (impressions: 1)
- `www.amazon.de/dp/B0G11LQ31S?tag=wobranding-21`  (impressions: 1)
- `s.click.aliexpress.com/s/pyFri10M6ltAv61YZY9TfrxiDaaFXRreuZWJMeLtD8jig1wPxn51K2eq59ds8iT5Wl5L3w5KJyrl7SjOO3B0oJ0Xjwnc7n8AQA7gf5qnT4sCyU05LNms9JvyWQNFHNKtzBcoBpSguMg3UBR1FOODkmGTloXosMhqhnKgzzuJPYPxewVvzupiAiKSJA5SK0iQRxmaQ7UPG0AP2HC7uLitVpvXIfjMl7RnsnN7B8FrGfP9TWP7emQeaXV90Bp9fLEiLeKHsRf9R2jgKD32Axm5na4bRJdkhGVyv3GcDgMjmYrrZWinWctR9gnPwA4o3mb96MNVbhftfJooohXiNcoqmkIEPa8THHUvhMmDotQgstotNQtbjmuS3iTKKlNR3TRVB9Vrz0VNHdcHnfFHwPccEhPeoBDEr0N0NVIWsmlQQg0vVBFNYJbWqJ7CMJWi1wEXnqWpFo5qkjQmNhDf36xZVdmolKSbCvnLjyFVmazWaKcDqzZSFy0tvWm6LvUHZghDuAYFj9cmGpasWgy9gngFsi03S8DWWTNLuibVkVpygQDPvWcLvZuAR6yAuQVU9QaD99gRzSEmtFLl4FzJvvjlK0rIyfW2tvqabAUZ6BdMy3hVGzKop63l7USadc0vpjGsBWfd9HDpvYAan2nhDcl5kcuUbZ0el2jFXSVVv2LZ2phAuDO5hqiGx8g3rQRR3F6v1vPS2Nw2SrE5jissp127gbYO7nyrVIwhBjnUOyCp3gtAWx98RDMTd933PKWWcVbOkoSEbw69AQTvicZ6Peek5UhO73yXLmwL9VwnFGusC43f6Y3twrGeS17ZjTUe5Bf3j42DQMbegceHlcEARqEiNU2tLdBrDugy8PXUolF4RTc633c2HWbYtliQd6wF5drqq8R1E8VsTZ15R2vqZTzL1aSeHIQgZp8ufjxmh1IRq1aMg3yl6CDJnOFuqdxE5gcUrBtTnZHUz6E2g546GC22PSdXlINRhGye359A27dEK4trOLu15QV7FGvIaBXEbkvFhMCWz4BW`  (impressions: 1)

## All tools exposed by this server
### `search_offers`
Preisvergleich wotablet.de: tagesaktuelle Bestpreise fuer Tablets aus vielen Shops (u. a. Amazon, eBay), mit Filtern, Vergleichen und Kaufratgebern. Nutze dieses Tool, wenn ein Nutzer nach Preis, Angebot, "guenstig", "wo kaufen" oder einem konkreten Tablet fragt. Liefert siteSearchUrl (aktuelle Preise ALLER Shops auf wotablet.de), browse (passende Vergleichsseiten, Ratgeber und Markenseiten) und products (Angebote von Partner-Shops, die eine Weitergabe erlauben – kann leer sein). Gib dem Nutzer die Links unveraendert weiter. EN: Today's best prices for Tablets in Germany from many shops. Returns siteSearchUrl (live prices from all shops on wotablet.de), matching comparison pages, buying guides and brand pages (browse) and partner offers (products, may be empty). Pass links on unchanged. Set language to the user's language (e.g. "en", "tr", "fr") to get pages in that language; the result field languages lists what the site offers.

### `find_pages`
Findet die passenden Seiten auf wotablet.de zu einer Frage rund um Tablets: Vergleichsseiten (z.B. nach Ausstattung oder Preisklasse), Ratgeber/Kaufberatung und Markenseiten – jeweils mit Titel, Kurzbeschreibung und Link. Ideal fuer "welcher Tablet ist gut fuer …", "worauf achten beim Kauf" oder "Modelle von <Marke>". EN: Finds matching pages on wotablet.de – comparisons, buying guides and brand pages with title, summary and link. Use for "which Tablet should I buy", "what to look for" or brand questions.

### `lookup_product`
Schlaegt ein Partner-Angebot aus search_offers per Produkt-ID (externalId) nach. EN: Looks up a partner offer from search_offers by its ID (externalId). Read-only.
