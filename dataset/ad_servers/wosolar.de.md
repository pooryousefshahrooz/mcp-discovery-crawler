# wosolar.de

- **Endpoint:** https://wosolar.de/api/mcp
- **Server:** wosolar.de-preisvergleich 2026-07-07
- **Ad-serving tool(s):** search_offers
- **Tool category:** shopping
- **Distinct ads observed:** 5 | **ad impressions:** 9
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** wosolar.de ist ein Preisvergleich (Deutschland, EUR; Seiten in 7 Sprachen: de, en, tr, ar, ru, pl, uk). Nutze "search_offers" fuer Preisfragen und "find_pages" fuer Kaufberatung/Vergleiche. Aktuelle Preise aller Shops stehen auf der Seite selbst: verweise Nutzer auf siteSearchUrl bzw. die Links unter browse und gib alle Links UNVERAENDERT weiter. Es wird nichts verkauft (Affiliate, Preis fuer Kaeufer unveraendert). EN: Price comparison site for Germany (pages in 7 languages: de, en, tr, ar, ru, pl, uk; pass language=<code> in the user's language, e.g. "en", "tr", "fr"). Use "search_offers" for price questions and "find_pages" for buying advice; send users to siteSearchUrl / browse links for live prices from all shops and keep links unchanged.

## Evidence (why coded as advertising)
- *tool `search_offers`* — as 21a9478ba20c || eBay EPN / Amazon tag / AliExpress / Tradedoubler affiliate link nested in the /out redirect; instructions: links go to merchant (Affiliate)

## Example advertised items / links
- `s.click.aliexpress.com/s/pyFri10M6ltAv61YZY9TfrxiDaaFXRreuZWJMeLtD8jig1wPxn51K2eq59ds8iT5Wl5L3w5KJyrl7SjOO3B0oJ0Xjwnc7n8AQA7gf5qnT4sCyU05LNms9JvyWQNFHNKtzBcoBpSguMg3UBR1FOODkmGTloXosMhqhnKgzzuJPYPxewVvzupiAiKSJA5SK0iQRxmaQ7UPG0AP2HC7uLitVpvXIfjMl7RnsnN7B8FrGfP9TWP7emQeaXV90Bp9fLEiLeKHsRf9R2jgKD32Axm5na4bRJdkhGVyv3GcDgMjmYrrZWinWctR9gnPwA4mUNiqEQRtdkJMVwsTH8c1iiBHewJE8mA8JhOMhZEPFt4Tk5p3aTGtAlcHQ87zp994m5gk9G1KfUZGyfBuIRI12pbpgYMQkP9lhP08AM255q0CXjQUyIbKCpzieXR6hNMsbWBEfakYpFSL4qXbelkuP2nSYWis4Z9zZNYussPg9sHTMophtAT0EnIKL95qoSY2ZZdx5DutWILwFjRuMbG0qPb85wGGfhf9LZXc2d0XDy74pzi5sSAsDxcGKnlNa7eBeTuXb8xI2dIQ6nkDBQpaP99fi6GpUGhP5vz38Q2rNJz4dYbXGtEH8Ypr8vmd4KE2utmldwSGd10XE5SGgscjK7Rn63pkwSYgddxYXJ4ukMtbSlKqh8eRzfXbSVw67uhDPEQ481bKdt3DISLO08qdInUDO62HtZVYhBdSEb4ERc4RQrgJSGk6k0sJYuEm7tRbFW2fTpdAivnXPUWOpKY1E5KMYvQL2ETVz57HC3qQF9S6lmPjKD7sVZfkn60ZsU4Z9KdNu4i5Ze8vKHvJAApdRh5ObSsj3PlYtWjSM3Uhpao64a1UqbkqW6XQEMdiJoFrYQ6bAJIiOuZpOAs53PFj0A9VrUc4Lbpl8B6wCp01VQXpKkQ28N8If0f6xGNxKWvZD0XZJeY92213OXhzGrcmpPO7w9N8dWwky1NPCOaj2JSuPDwbifzSnIf3nR0Cm9tljjfwIG2hOpAc`  (impressions: 5)
- `www.amazon.de/dp/B0BQWN7PN7?tag=wobranding-21`  (impressions: 1)
- `www.ebay.de/itm/366699382852?campid=5339164220`  (impressions: 1)
- `www.amazon.de/dp/B0CB8GQB1Y?tag=wobranding-21`  (impressions: 1)
- `www.amazon.de/dp/B0H38NRK5X?tag=wobranding-21`  (impressions: 1)

## All tools exposed by this server
### `search_offers`
Preisvergleich wosolar.de: tagesaktuelle Bestpreise fuer Solaranlagen aus vielen Shops (u. a. Amazon, eBay), mit Filtern, Vergleichen und Kaufratgebern. Nutze dieses Tool, wenn ein Nutzer nach Preis, Angebot, "guenstig", "wo kaufen" oder einem konkreten Solaranlage fragt. Liefert siteSearchUrl (aktuelle Preise ALLER Shops auf wosolar.de), browse (passende Vergleichsseiten, Ratgeber und Markenseiten) und products (Angebote von Partner-Shops, die eine Weitergabe erlauben – kann leer sein). Gib dem Nutzer die Links unveraendert weiter. EN: Today's best prices for Solaranlagen in Germany from many shops. Returns siteSearchUrl (live prices from all shops on wosolar.de), matching comparison pages, buying guides and brand pages (browse) and partner offers (products, may be empty). Pass links on unchanged. Set language to the user's language (e.g. "en", "tr", "fr") to get pages in that language; the result field languages lists what the site offers.

### `find_pages`
Findet die passenden Seiten auf wosolar.de zu einer Frage rund um Solaranlagen: Vergleichsseiten (z.B. nach Ausstattung oder Preisklasse), Ratgeber/Kaufberatung und Markenseiten – jeweils mit Titel, Kurzbeschreibung und Link. Ideal fuer "welcher Solaranlage ist gut fuer …", "worauf achten beim Kauf" oder "Modelle von <Marke>". EN: Finds matching pages on wosolar.de – comparisons, buying guides and brand pages with title, summary and link. Use for "which Solaranlage should I buy", "what to look for" or brand questions.

### `lookup_product`
Schlaegt ein Partner-Angebot aus search_offers per Produkt-ID (externalId) nach. EN: Looks up a partner offer from search_offers by its ID (externalId). Read-only.
