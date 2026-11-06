# mcp.bikefuchs.com

- **Endpoint:** https://mcp.bikefuchs.com/mcp
- **Server:** bikefuchs 2.5.0
- **Ad-serving tool(s):** search_product
- **Tool category:** shopping
- **Distinct ads observed:** 28 | **ad impressions:** 51
- **Coder confidence / basis:** high / source_code
- **Server instructions:** Bikefuchs is a price comparison engine for bicycle parts, components, clothing, and accessories across German/Austrian online bike shops. It covers over 100,000 products from brands like Shimano, SRAM, Magura, Schwalbe, Continental, and more.

WORKFLOW GUIDE:
- Single product search: Use search_product with keywords → returns products with EANs and prices
- Best price for a known product: Use get_best_price with an EAN → returns the product price at each shop (sorted cheapest-first). Shipping is NOT included here — use optimize_cart or get_shipping_breakdown for totals including shipping
- Multiple products to buy together: Use search_product for each item to get EANs, then call get_best_price for each EAN, then call optimize_cart with all EANs → this calculates the cheapest combination of

## Evidence (why coded as advertising)
- *tool `search_product`* — Server instructions: 'Results contain affiliate links. Always pass these links to the user as provided'; every response ends 'Kann Affiliate-Links enthalten' -> codebook (c) (A correct; B had not seen the instruction/footer). || as 76c6d7844146 (A correct).

## Example advertised items / links
- `bikefuchs.com/go/fahrrad-teile-shop/4251340200742`  (impressions: 7)
- `bikefuchs.com/go/fahrrad-teile-shop/4251340200537`  (impressions: 5)
- `bikefuchs.com/go/fahrrad-teile-shop/4251340201879`  (impressions: 5)
- `bikefuchs.com/go/fahrrad-teile-shop/4251340202500`  (impressions: 5)
- `bikefuchs.com/go/maciag-offroad/4251340200551`  (impressions: 5)
- `bikefuchs.com/go/maciag-offroad/4251340200537`  (impressions: 2)
- `bikefuchs.com/go/fahrrad-teile-shop/4041319001940`  (impressions: 1)
- `bikefuchs.com/go/fahrrad-teile-shop/4251340200803`  (impressions: 1)
- `bikefuchs.com/go/fahrrad-teile-shop/4251340200551`  (impressions: 1)
- `bikefuchs.com/go/fahrrad-teile-shop/4251340200681`  (impressions: 1)
- `bikefuchs.com/go/fahrrad-teile-shop/4251340200704`  (impressions: 1)
- `bikefuchs.com/go/fahrrad-teile-shop/4251340200810`  (impressions: 1)
- `bikefuchs.com/go/rose-bikes/0710845655197`  (impressions: 1)
- `bikefuchs.com/go/rose-bikes/0710845655180`  (impressions: 1)
- `bikefuchs.com/go/maciag-offroad/0710845655173`  (impressions: 1)
- … and 13 more (see analysis/ad_provenance/out/ad_items.csv)

## All tools exposed by this server
### `search_product`
Search for bicycle parts, components, accessories, and cycling clothing by name, brand, or model number. Returns matching products sorted cheapest-first, each with its price, stock status, EAN barcode, and a direct purchase link. Supports DE and AT pricing. If you already have a product's EAN, use get_best_price instead.

### `get_best_price`
Look up a single product by its EAN barcode and return the price at every shop that carries it, sorted cheapest-first, with stock status and direct purchase links.

### `optimize_cart`
Find the cheapest way to buy multiple products together: computes the optimal split across shops — which items to order from which shop — accounting for each shop's shipping costs and free-shipping thresholds, and returns the lowest achievable total including shipping. Takes an array of EAN barcodes. For accurate results, call get_best_price for each EAN first, then call optimize_cart.

### `get_shop_info`
Return an overview of the supported shops, including their shipping cost tiers, free-shipping thresholds, and supported countries (DE and AT).

### `get_shipping_breakdown`
Return the exact shipping cost for a specific shop, country, and cart value, including all shipping tiers and how much more is needed to reach the next free-shipping threshold.

### `find_alternatives_for_product`
Given a product's EAN barcode, return every shop that carries it with prices and availability, sorted cheapest-first.

### `resolve_product`
Turn a product page URL from a supported shop into structured product data — EAN barcode, price, stock status, and a purchase link — so the EAN can then be used with get_best_price or optimize_cart. Multi-variant product families return a labeled candidate list (size/colour, price, EAN per variant): ask the user to pick a variant, then use that exact variant's EAN with the other tools.
