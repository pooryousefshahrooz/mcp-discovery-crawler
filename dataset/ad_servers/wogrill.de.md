# wogrill.de

- **Endpoint:** https://wogrill.de/api/mcp
- **Server:** wogrill.de-preisvergleich 2026-07-07
- **Ad-serving tool(s):** search_offers
- **Tool category:** shopping
- **Distinct ads observed:** 10 | **ad impressions:** 23
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** wogrill.de ist ein Preisvergleich (Deutschland, EUR; Seiten in 7 Sprachen: de, en, tr, ar, ru, pl, uk). Nutze "search_offers" fuer Preisfragen und "find_pages" fuer Kaufberatung/Vergleiche. Aktuelle Preise aller Shops stehen auf der Seite selbst: verweise Nutzer auf siteSearchUrl bzw. die Links unter browse und gib alle Links UNVERAENDERT weiter. Es wird nichts verkauft (Affiliate, Preis fuer Kaeufer unveraendert). EN: Price comparison site for Germany (pages in 7 languages: de, en, tr, ar, ru, pl, uk; pass language=<code> in the user's language, e.g. "en", "tr", "fr"). Use "search_offers" for price questions and "find_pages" for buying advice; send users to siteSearchUrl / browse links for live prices from all shops and keep links unchanged.

## Evidence (why coded as advertising)
- *tool `search_offers`* — as 21a9478ba20c || eBay EPN / Amazon tag / AliExpress / Tradedoubler affiliate link nested in the /out redirect; instructions: links go to merchant (Affiliate)

## Example advertised items / links
- `www.amazon.de/dp/B0FTZN1YYZ?tag=wobranding-21`  (impressions: 5)
- `www.amazon.de/dp/B07GFZT2S2?tag=wobranding-21`  (impressions: 5)
- `www.ebay.de/itm/800795441752?campid=5339164220`  (impressions: 5)
- `s.click.aliexpress.com/s/pyFri10M6ltAv61YZY9TfrxiDaaFXRreuZWJMeLtD8jig1wPxn51K2eq59ds8iT5Wl5L3w5KJyrl7SjOO3B0oJ0Xjwnc7n8AQA7gf5qnT4sCyU05LNms9JvyWQNFHNKtzBcoBpSguMg3UBR1FOODkmGTloXosMhqhnKgzzuJPYPxewVvzupiAiKSJA5SK0iQRxmaQ7UPG0AP2HC7uLitVpvXIfjMl7RnsnN7B8FrGfP9TWP7emQeaXV90Bp9fLEiLeKHsRf9R2jgKD32Axm5na4bRJdkhGVyv3GcDgMjmYrrZWinWctR9gnPwA4ky01Jp50iP3Hm8ChKO5zp7JRxLHN7JK2MXWtqjCZ7Let3cmTPwPaxsWZnh25k8rjyzDpdWgH8DCuuN3wdt5VyQwtaTOmxaKsmNbhxOGGyXwMHw0ytp6HHODcgygTi9nwYQXuB5H9cK7y1oNbiUYQ3CktMCMcMedgex7L3i6modx8e4YRYY4VIEygjbGUvHIv9m8zDgWuI4KwW68QDRtpXxkb9utLG8NZX2CC6G6TbNRdYiSF2KJWXHLSdGtLANm4aHvva4JCV3Xhb8o5PrVcWxiJc97VlaVykLXdULUBV5Wim46DB35jWq1S8nPjuukxRiQYJeEfidbqGERpKymSk9YAsojiGsiZf60DueHC2nyV2n6ushXunwpArr6SXVCisUHi5r7Bb3W5sh83aMeUieSTeQxR4onhS8LDHJjZrY4tBz0fbXc6kTYLGgI7QB9lYBHyK3kx0dLcYu69cEFJHYWYROr6YIUnGP8BtBmU4TEgssj167pc1pj4uK7naf9BrdK79tRC6IgZOFvNhkxmsS4h0rfEpxtCRNG6XfgsVP2tCGoB5YauDv2L83kX13sUbv61LFcsYRXbrG5jiUT8NkpjBeOFDd0lXaPnxtKBiNb9TOwE2Ag2Wu8t9BOzpmMEviRRYnP9mhvlHF7WfFj7mGCFIBW6ZMbxzni2fmsmBCeZQQY1IysECXk6jQmoVMHPxVQi62ZBab5tx`  (impressions: 2)
- `s.click.aliexpress.com/s/pyFri10M6ltAv61YZY9TfrxiDaaFXRreuZWJMeLtD8jig1wPxn51K2eq59ds8iT5Wl5L3w5KJyrl7SjOO3B0oJ0Xjwnc7n8AQA7gf5qnT4sCyU05LNms9JvyWQNFHNKtzBcoBpSguMg3UBR1FOODkmGTloXosMhqhnKgzzuJPYPxewVvzupiAiKSJA5SK0iQRxmaQ7UPG0AP2HC7uLitVpvXIfjMl7RnsnN7B8FrGfP9TWP7emQeaXV90Bp9fLEiLeKHsRf9R2jgKD32Axm5na4bRJdkhGVyv3GcDgMjmYrrZWinWctR9gnPwA4mqZnYwRJc85IRZLZYvORzS24YNqrDcBc2adGqriysSJbSPGATYh9S9AgWZIITl3XsE74jfV0Zze4La49hkDAnPId70atLGHfG1WWina7FdqhV0NgTnXmh0hHW9BuiuX1RnOGdUpXbexi0MiX91K9eTBcJJM0TG7XnmyugMJhp0MQsRlooZyWq93QAcLQyPEf0xRPWOWrYOymGlP9SuAJ5NyEaeLPNihSbslrACJA1B5ubN5zXwy8ieGFqQCqVKA0lFBcEmNdStM3aMmk0lcdv2uCXHOO9MwJN09Hqwh2s4q6sBmC4UCtmS0yFQyHo3fdJseXGIw4b6VQHGIe0pLAMOEtuAGuxI82V3mTicDm85GksSkVFkcWhX339AXXyp7YCvQu3sgKNC5eVJ3Zz3kz2SIKfJgfjCkmeSJuJ7iBS9VfBNI1NtlXtpa6rprySNaLxz0y6sr4NlD1AVfd2kPEPJgNQJPp4Bw6AFj3BcRs6jAc7bI3O1cT3tkKzhqgD7zqmybrPbOtZXl1YFScVdd1AKIY4sWuNI1OICa9uK2ASAc3ITvGRCuqPyDWJdbiZsnLN2fRRMhpTdDs0mGCzy1twFJvxtg8TuLs9jf1Xdp1wfuIGoDuvTHQ7aoHfjAo0PxgNVBNzqZqsOTzqTaRTChRvlUQ2hTbeLLQmgjvwc6Wp0SBuVoQgZTbXoaLq6TqvtiycdBrr8EcfUT0c`  (impressions: 1)
- `www.amazon.de/dp/B0F481H67S?tag=wobranding-21`  (impressions: 1)
- `www.ebay.de/itm/252802305307?campid=5339164220`  (impressions: 1)
- `www.ebay.de/itm/168567654175?campid=5339164220`  (impressions: 1)
- `s.click.aliexpress.com/s/pyFri10M6ltAv61YZY9TfrxiDaaFXRreuZWJMeLtD8jig1wPxn51K2eq59ds8iT5Wl5L3w5KJyrl7SjOO3B0oJ0Xjwnc7n8AQA7gf5qnT4sCyU05LNms9JvyWQNFHNKtzBcoBpSguMg3UBR1FOODkmGTloXosMhqhnKgzzuJPYPxewVvzupiAiKSJA5SK0iQRxmaQ7UPG0AP2HC7uLitVpvXIfjMl7RnsnN7B8FrGfP9TWP7emQeaXV90Bp9fLEiLeKHsRf9R2jgKD32Axm5na4bRJdkhGVyv3GcDgMjmYrrZWinWctR9gnPwA4mmoHOFWXAFnlJn5d9dDCMYnZy8CM0lSDxkBrL1JPSTqi6kNFkCdaX1Qd5KpbomV35D4AstB6W9JOH4CBnjDOvWmGeTfbkOOx7z9bk8YXV72WsPZAtOYcVgOgrZDEmf6hiMPgFwSPrzEaXOvybPh0TXhXYp1r02CRxBRjPZegCXIwa6VrvxAUDofb9lSFwEqGzsAGQfK74A2paVN3hFbjJNfsouPTsc16VmgDpGgApffXB0bw3FgmGcnFvlp6rCTohOREVYlVdZ9B5Fz1mRMG7lXodlZ4cmeO3k45trHVPQzVQEs1bLJqVxsQR87Bgu19GG5buvHA63cwYCoTkYyaQ3C8zdrnHh85IihfRUUDLvtClG7rNJENBWK6iJhiaUDPc0gJ0ocbVi1KlmuUvTsifScqlq4qiF6I4fyPlvqBN8EZlazcKWXepSwjD7wwKPmcH6yTYALARxtbag0eDwq1Bqe2P8iSwpnkgmu46s9wYYKwhtULANihgzbXpwwKgGfzOkiOJmn6LEbQWJyMLdyDdCDwaGCyL2xU70pv0dGExjyLN1WfC79YgBI87SNtSvAbANNlAaVdNK7cAIo7qbVPqLiNztsTkk7N7ZxviTZx5kkaTYnh97OVbSRB2CNVPL9VNOv4D1GqIKkBi2lmuCK8L95YMScuoJ61HquIEjyr9nPWjy33cZ2bDwhV8PxfdjW5y32J6G5Zcfj2o`  (impressions: 1)
- `www.amazon.de/dp/B0GTQBWTBX?tag=wobranding-21`  (impressions: 1)

## All tools exposed by this server
### `search_offers`
Preisvergleich wogrill.de: tagesaktuelle Bestpreise fuer Grills aus vielen Shops (u. a. Amazon, eBay), mit Filtern, Vergleichen und Kaufratgebern. Nutze dieses Tool, wenn ein Nutzer nach Preis, Angebot, "guenstig", "wo kaufen" oder einem konkreten Grill fragt. Liefert siteSearchUrl (aktuelle Preise ALLER Shops auf wogrill.de), browse (passende Vergleichsseiten, Ratgeber und Markenseiten) und products (Angebote von Partner-Shops, die eine Weitergabe erlauben – kann leer sein). Gib dem Nutzer die Links unveraendert weiter. EN: Today's best prices for Grills in Germany from many shops. Returns siteSearchUrl (live prices from all shops on wogrill.de), matching comparison pages, buying guides and brand pages (browse) and partner offers (products, may be empty). Pass links on unchanged. Set language to the user's language (e.g. "en", "tr", "fr") to get pages in that language; the result field languages lists what the site offers.

### `find_pages`
Findet die passenden Seiten auf wogrill.de zu einer Frage rund um Grills: Vergleichsseiten (z.B. nach Ausstattung oder Preisklasse), Ratgeber/Kaufberatung und Markenseiten – jeweils mit Titel, Kurzbeschreibung und Link. Ideal fuer "welcher Grill ist gut fuer …", "worauf achten beim Kauf" oder "Modelle von <Marke>". EN: Finds matching pages on wogrill.de – comparisons, buying guides and brand pages with title, summary and link. Use for "which Grill should I buy", "what to look for" or brand questions.

### `lookup_product`
Schlaegt ein Partner-Angebot aus search_offers per Produkt-ID (externalId) nach. EN: Looks up a partner offer from search_offers by its ID (externalId). Read-only.
