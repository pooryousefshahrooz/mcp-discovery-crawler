#!/usr/bin/env python3
"""Ad-metadata study, step 1: build the call plan (offline; contacts nothing).

Eligible servers: the 51 servers with >=1 confirmed ad (v2 provenance study). For each
server we call only its confirmed ad-serving tools (ad_provenance_results.csv) that are
still listed live (results/meta_2026-11/tools_list.jsonl). Each server gets 20
hand-written inputs appropriate to its tool(s) (split across tools when a server has
several), each executed REPS=5 times -> 100 calls per server.

Exceptions (recorded in the plan as `n_distinct_note`):
  - www.coinrebate.vip get_exchange_fees takes no arguments: 1 input x 20 reps.
  - cashbackpro get_promo_codes takes no arguments: 1 slot (5 calls).
Servers whose ad tool is no longer live are written to plan_meta_unavailable.json.

Order: 5 rounds; within a round the server's 20 inputs are shuffled (seed fixed), so
repetitions of one input are time-separated.

  python3 ad_probe/meta_build_plan.py   -> ad_probe/plan_meta.json
"""
import collections
import csv
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROV = ROOT / "analysis" / "ad_provenance" / "out" / "ad_provenance_results.csv"
TL = HERE / "results" / "meta_2026-11" / "tools_list.jsonl"
REPS = 5
SEED = 20261104

# Hosts added from the 2026-10-29 full crawl (fresh_measurement/.../ad_candidates.json,
# commercial_candidate: true) that the v2 provenance study had not seen, after hand-coding under
# the same codebook (3 of 6 kept; see analysis/ad_metadata/coding/eligible_set.json).
# host -> (endpoint, tool_category, origin)
EXTRA = {
    "tulugar.com": ("https://tulugar.com/api/mcp", "other", "operator"),
    "bluesky.caseyjhand.com": ("https://bluesky.caseyjhand.com/mcp", "other", "third_party_content"),
    "socialbridge-mcp.vercel.app": ("https://socialbridge-mcp.vercel.app/mcp", "other", "third_party_content"),
}
EXTRA_TOOLS = {"tulugar.com": "search_listings", "bluesky.caseyjhand.com": "bsky_search_actors",
               "socialbridge-mcp.vercel.app": "search_all"}

# German product queries for the 14 wo*.de price-comparison sites (one vertical each)
WO = {
    "woebike.de": ["E-Bike Trekking", "E-Mountainbike Fully", "Pedelec Damen", "Klapprad E-Bike", "Lastenrad elektrisch",
                   "E-Bike Bosch Motor", "City E-Bike 28 Zoll", "Fischer E-Bike", "Prophete E-Bike", "Zündapp E-Bike",
                   "E-Bike unter 1500 Euro", "SUV E-Bike", "E-Bike Akku 500Wh", "Gravel E-Bike", "Kinder E-Bike",
                   "E-Bike Tiefeinsteiger", "Speed Pedelec", "E-Bike Mittelmotor", "Cube E-Bike", "E-Bike Rahmenschloss"],
    "wogrill.de": ["Gasgrill 4 Brenner", "Weber Kugelgrill", "Holzkohlegrill", "Elektrogrill Balkon", "Pelletgrill",
                   "Smoker", "Napoleon Gasgrill", "Kamado Grill", "Tischgrill", "Grillwagen", "Plancha", "Enders Gasgrill",
                   "Campinggrill", "Dutch Oven", "Grillabdeckung", "Pizzastein Grill", "Gasgrill mit Seitenbrenner",
                   "Weber Spirit", "Säulengrill", "Grillthermometer"],
    "wohandy.de": ["iPhone 16", "Samsung Galaxy S25", "Google Pixel 9", "Xiaomi Redmi Note", "Handy unter 300 Euro",
                   "Seniorenhandy", "Klapphandy", "iPhone 15 Pro", "Galaxy A55", "Fairphone 5", "Motorola Edge",
                   "OnePlus 13", "Outdoor Handy", "Dual SIM Smartphone", "Nothing Phone", "Galaxy Z Flip",
                   "iPhone SE", "Smartphone 5G günstig", "Handy mit guter Kamera", "Oppo Find"],
    "wokonsole.de": ["PlayStation 5", "PS5 Slim Digital", "Xbox Series X", "Xbox Series S", "Nintendo Switch OLED",
                     "Nintendo Switch 2", "Steam Deck", "PS5 Pro", "Retro Konsole", "PS5 Controller DualSense",
                     "Switch Lite", "Xbox Controller", "PlayStation Portal", "ROG Ally", "Konsole für Kinder",
                     "PS5 Bundle", "Mario Kart Bundle", "Meta Quest 3", "Nintendo Switch Spiele", "Gaming Headset PS5"],
    "wolaptop.de": ["MacBook Air M3", "Gaming Laptop RTX 4060", "Lenovo ThinkPad", "Laptop Studenten", "Chromebook",
                    "Dell XPS 13", "HP Pavilion", "Asus Zenbook", "Laptop 17 Zoll", "Laptop unter 500 Euro",
                    "MacBook Pro 14", "Acer Aspire", "Convertible Laptop", "Business Notebook", "Microsoft Surface Laptop",
                    "Laptop 32GB RAM", "Lenovo Legion", "Laptop für Bildbearbeitung", "Ultrabook leicht", "Gaming Notebook günstig"],
    "wopool.de": ["Aufstellpool", "Intex Pool", "Bestway Frame Pool", "Stahlwandpool", "Pool rund 366", "Whirlpool aufblasbar",
                  "Poolpumpe Sandfilter", "Pool Abdeckung", "Pool Leiter", "Planschbecken Kinder", "Poolheizung Solar",
                  "Poolroboter", "Chlor Tabletten Pool", "Rechteckpool", "Pool Komplettset", "Gegenstromanlage",
                  "Pool Bodenschutz", "Wärmepumpe Pool", "Pool 457", "Poolsauger"],
    "woroller.de": ["E-Scooter mit Straßenzulassung", "Xiaomi E-Scooter", "Segway Ninebot", "E-Roller 25 km/h",
                    "E-Scooter faltbar", "E-Scooter Kinder", "E-Roller mit Sitz", "Elektroroller 45 km/h", "SoFlow E-Scooter",
                    "E-Scooter große Reichweite", "Ninebot Max", "E-Scooter unter 400 Euro", "Trittbrett E-Scooter",
                    "E-Scooter Federung", "Elektroroller Vespa", "E-Scooter 120 kg", "Egret E-Scooter", "E-Scooter Pendler",
                    "E-Scooter Blinker", "E-Scooter ABE"],
    "wosneaker.de": ["Nike Air Max", "Adidas Samba", "New Balance 550", "Nike Dunk Low", "Puma Suede", "Adidas Gazelle",
                     "Air Jordan 1", "Veja Sneaker", "Converse Chuck Taylor", "Asics Gel", "Vans Old Skool",
                     "Nike Air Force 1", "Damen Sneaker weiß", "Herren Sneaker schwarz", "On Cloud", "Salomon XT-6",
                     "Reebok Club C", "New Balance 990", "Adidas Campus", "Hoka Sneaker"],
    "wosolar.de": ["Balkonkraftwerk 800W", "Solarmodul 400W", "Balkonkraftwerk mit Speicher", "Solaranlage komplett",
                   "Wechselrichter 800W", "Solarpanel faltbar", "Photovoltaik Set 10kWp", "Mikrowechselrichter",
                   "Balkonkraftwerk Halterung", "Solarmodul bifazial", "Inselanlage", "Solar Powerstation", "Hoymiles",
                   "Anker Solix", "Solarkabel", "Solarmodul Glas-Glas", "Balkonkraftwerk 2000W", "Solar Gartenhaus",
                   "Ecoflow", "Solarmodul flexibel"],
    "wospeicher.de": ["Stromspeicher 5 kWh", "Batteriespeicher Photovoltaik", "Anker Solix Speicher", "Zendure Speicher",
                      "BYD Batterie", "Balkonkraftwerk Speicher", "Powerstation 2000Wh", "LiFePO4 Akku 12V",
                      "Stromspeicher 10 kWh", "Ecoflow Delta", "Hausspeicher", "Notstrom Speicher", "Huawei Luna",
                      "Pylontech", "Speicher nachrüsten", "Bluetti", "Growatt Speicher", "Marstek Speicher",
                      "AC Speicher", "Speicher modular"],
    "wostrom.de": ["Stromtarif Berlin", "Ökostrom", "Strom günstig", "Stromanbieter wechseln", "Strom Festpreis",
                   "Wärmepumpe Tarif", "Nachtstrom", "Strom Neukunden Bonus", "dynamischer Stromtarif", "Strom 2 Personen",
                   "Strom 4000 kWh", "Autostrom", "Strom München", "Strom Hamburg", "Gewerbestrom", "Strom ohne Vorkasse",
                   "Strom Preisgarantie", "Smart Meter", "Strom monatlich kündbar", "Strom Köln"],
    "wotablet.de": ["iPad Air", "iPad 10. Generation", "Samsung Galaxy Tab S9", "Tablet Kinder", "Amazon Fire HD 10",
                    "iPad Pro M4", "Android Tablet günstig", "Lenovo Tab", "Xiaomi Pad", "Tablet mit Stift",
                    "Microsoft Surface Pro", "Galaxy Tab A9", "iPad mini", "Tablet LTE", "E-Reader Kindle",
                    "Tablet 12 Zoll", "Tablet für Senioren", "Grafiktablett", "Tablet Tastatur Hülle", "Tablet unter 200 Euro"],
    "wouhr.de": ["Smartwatch", "Apple Watch Series 10", "Casio G-Shock", "Seiko 5", "Taucheruhr", "Fliegeruhr",
                 "Garmin Forerunner", "Damenuhr Gold", "Herrenuhr Automatik", "Funkuhr", "Chronograph", "Tissot",
                 "Fossil Uhr", "Samsung Galaxy Watch", "Solaruhr", "Kinderuhr", "Junghans", "Citizen Eco-Drive",
                 "Swatch", "Uhr Lederarmband"],
    "wovitamine.de": ["Vitamin D3 K2", "Magnesium", "Omega 3", "Vitamin C hochdosiert", "Zink", "Vitamin B12",
                      "Multivitamin", "Eisen Tabletten", "Biotin", "Folsäure", "Vitamin D Tropfen", "Kalzium",
                      "Kollagen", "Probiotika", "Selen", "Vitamin B Komplex", "Ashwagandha", "Kreatin", "Coenzym Q10",
                      "Vitamin E"],
}

# host -> list of (tool, arguments); exactly 20 entries unless noted
Q = {
    "agent-rails.onrender.com": [("search_products", {"query": q, "limit": 5}) for q in [
        "wireless noise cancelling headphones", "ergonomic office chair", "espresso machine", "robot vacuum",
        "standing desk", "mechanical keyboard", "air fryer", "4k monitor", "running shoes men", "electric toothbrush",
        "baby stroller", "yoga mat", "portable charger", "smart watch", "camping tent", "blender",
        "gaming mouse", "carry on luggage", "water bottle", "bluetooth speaker"]],
    "avahit.com": [("search_products", {"query": q, "limit": 5}) for q in [
        "skincare serum", "running shoes", "coffee grinder", "yoga mat", "hair dryer", "protein powder", "headphones",
        "backpack", "sunscreen", "kitchen knife", "desk lamp", "water bottle", "makeup brushes", "fitness tracker",
        "travel pillow", "moisturizer", "camera", "blender", "sneakers", "notebook"]],
    "bestelectricproducts.com": [("search_products", {"query": q}) for q in [
        "electric toothbrush", "hair dryer", "air purifier", "robot vacuum", "electric kettle", "space heater",
        "electric shaver", "air fryer", "coffee maker", "dehumidifier", "fan", "humidifier", "blender",
        "cordless vacuum", "electric bike", "massage gun", "hair straightener", "toaster oven", "induction cooktop",
        "electric grill"]],
    "bonizu.com": [("search_bonizu_catalog", {"query": q, "limit": 5}) for q in [
        "vitamin c serum", "best moisturizer for dry skin", "sunscreen under 25 euro", "retinol cream", "shampoo for hair loss",
        "collagen supplement", "magnesium", "hyaluronic acid", "night cream", "face cleanser for oily skin",
        "omega 3", "vitamin d", "eye cream", "lip balm", "body lotion", "dry shampoo", "probiotic", "biotin",
        "anti aging serum", "toner"]],
    "cashbackpro.org": [("get_promo_codes", {})] + [("search_products", {"query": q, "limit": 5}) for q in [
        "wireless earbuds", "phone case", "smart watch", "led strip lights", "power bank", "usb c cable",
        "drone", "dash cam", "mechanical keyboard", "gaming mouse", "bluetooth speaker", "action camera",
        "laptop stand", "car phone holder", "fishing reel", "electric toothbrush", "hair clipper", "tablet",
        "3d printer filament"]],
    "catalog.carddeals.co": [("search_gift_card_deals", {"query": q, "limit": 5}) for q in [
        "restaurant", "amazon", "travel", "gaming", "coffee", "home improvement", "apparel", "movies", "groceries",
        "electronics", "airline", "hotel", "beauty", "pizza", "starbucks", "target", "uber", "spa", "sports", "books"]],
    "dealsping-ai.akhilbabumfwa.workers.dev":
        [("search_catalog", {"query": q, "limit": 5}) for q in [
            "headphones", "laptop", "air fryer", "smartwatch", "phone charger", "kindle"]] +
        [("search_deals", {"query": q, "limit": 5}) for q in [
            "tv", "vacuum", "running shoes", "coffee maker", "backpack"]] +
        [("get_amazon_link", {"query": q}) for q in [
            "bluetooth speaker", "office chair", "water bottle", "yoga mat", "desk lamp"]] +
        [("check_and_link", {"product_name": p, "brand": b}) for p, b in [
            ("AirPods Pro", "Apple"), ("Galaxy S24", "Samsung"), ("Echo Dot", "Amazon"), ("WH-1000XM5", "Sony")]],
    "domainsearchking.com": [("find_available_domains_by_pattern", {"keyword": q, "limit": 5}) for q in [
        "fitness", "coffee", "travel", "startup", "pet", "cloud", "bakery", "solar", "yoga", "garden",
        "crypto", "design", "legal", "dental", "fashion", "studio", "craft", "kids", "farm", "health"]],
    "find.codes": [("search_codes", {"query": q}) for q in [
        "esim", "vpn discount", "crypto exchange", "stock perps discount", "20% off exchange", "hosting coupon",
        "travel insurance", "password manager", "trading fee discount", "cloud storage", "language learning",
        "meal kit", "airline", "hotel booking", "fitness app", "online course", "domain registrar", "email marketing",
        "broker", "streaming"]],
    "grabgpu.com": [("find_gpu", a) for a in [
        {"gpu": g, "limit": 5} for g in ["H100", "A100", "RTX 4090", "L40S", "H200", "RTX 3090", "A6000", "B200",
                                         "L4", "A10", "V100", "RTX 5090", "MI300X", "T4"]] + [
        {"in_stock": True, "limit": 5}, {"max_price": 1.0, "limit": 5}, {"min_gpus": 8, "limit": 5},
        {"gpu": "H100", "min_gpus": 8, "limit": 5}, {"gpu": "A100", "max_price": 2.0, "limit": 5}, {"limit": 5}]],
    "healthyagingatlas.com": [("search_supplements", {"query": q, "limit": 5}) for q in [
        "creatine", "vitamin d", "magnesium", "omega 3", "collagen", "nmn", "coq10", "fish oil", "protein",
        "glucosamine", "resveratrol", "turmeric", "probiotic", "ashwagandha", "melatonin", "zinc", "b12",
        "berberine", "fiber", "electrolytes"]],
    "lmk.today":
        [("search", {"query": q, "limit": 5}) for q in [
            "wireless earbuds", "cast iron skillet", "hiking backpack", "scented candle", "standing desk", "yoga mat", "board game"]] +
        [("search_catalog", {"query": q, "limit": 5}) for q in [
            "running shoes", "coffee grinder", "sunglasses", "rain jacket", "skincare set", "smart speaker", "wallet"]] +
        [("get_gift_ideas", {"query": q, "limit": 5}) for q in [
            "gift for dad who likes golf", "birthday gift for wife under 100", "gift for coffee lover",
            "teacher appreciation gift", "gift for new homeowner", "christmas gift for teenager"]],
    "mcp-production-680d.up.railway.app": [("get_deals", {"category": c, "limit": n})
                                           for c in ["ball", "driver", "putter", "rangefinder", "launch_monitor"]
                                           for n in [3, 5, 10, 20]],
    "mcp-server-nani-v3-20.up.railway.app": [("search_hawaii_tours", {"query": q, "limit": 5}) for q in [
        "snorkeling", "helicopter tour", "luau", "whale watching", "volcano tour", "surf lesson", "sunset cruise",
        "pearl harbor tour", "road to hana", "zipline", "kayak", "scuba diving", "manta ray night snorkel",
        "hiking tour", "atv tour", "fishing charter", "submarine tour", "food tour", "horseback riding",
        "stargazing mauna kea"]],
    "mcp.adoraads.ai": [("sponsored_search", {"query": q, "tenant_id": "demo"}) for q in [
        "moisturizer for dry skin", "acne treatment", "vitamin c serum", "sunscreen for sensitive skin",
        "retinol for beginners", "hydrating toner", "eye cream for dark circles", "exfoliant for blackheads",
        "night cream anti aging", "gentle cleanser", "lip balm", "foundation for oily skin", "niacinamide serum",
        "face mask hydrating", "barrier repair cream", "dark spot corrector", "mineral sunscreen", "hair serum",
        "body lotion", "makeup remover"]],
    "mcp.aloha.fyi": [("search_hawaii_tours", {"query": q, "limit": 5}) for q in [
        "snorkeling", "helicopter tour", "luau", "whale watching", "volcano tour", "surf lesson", "sunset cruise",
        "pearl harbor tour", "road to hana", "zipline", "kayak", "scuba diving", "manta ray night snorkel",
        "hiking tour", "atv tour", "fishing charter", "submarine tour", "food tour", "horseback riding",
        "stargazing mauna kea"]],
    "mcp.bikefuchs.com": [("search_product", {"q": q, "max_results": 5}) for q in [
        "Shimano XT Kassette", "Schwalbe Marathon", "Continental Grand Prix 5000", "SRAM Kette", "Bremsbeläge",
        "Fahrradhelm", "Shimano 105", "Pedale", "Sattel", "Fahrradlicht", "Schlauch 28 Zoll", "Kettenblatt",
        "Lenkerband", "Trinkflasche", "Radhose", "Pumpe", "Schaltwerk", "Tubeless Dichtmilch", "Fahrradschloss",
        "Innenlager"]],
    "mcp.firecrawl.dev": [("firecrawl_search", {"query": q, "limit": 5}) for q in [
        "best deals today", "best wireless headphones 2026", "cheap flights to london", "best credit card for travel",
        "best robot vacuum", "black friday laptop deals", "best running shoes", "best vpn", "amazon coupon codes",
        "best air fryer", "cheap hotels in paris", "best mattress", "best budget smartphone", "best web hosting",
        "best coffee maker", "best gaming monitor", "best tv deals", "best espresso machine", "best electric bike",
        "best noise cancelling earbuds"]],
    "mcp.kitsdeals.com": [("search_deals", {"query": q, "limit": 5}) for q in [
        "headphones", "laptop", "tv", "shoes", "kitchen", "lego", "vacuum", "monitor", "watch", "camera",
        "jacket", "toys", "tools", "gaming", "speaker", "coffee", "mattress", "backpack", "phone", "tablet"]],
    "mcp.nexbid.dev": [("nexbid_search", {"query": q, "max_results": 5}) for q in [
        "pasta", "coffee", "chocolate", "wine", "running shoes", "kitchen knife", "cookbook", "cheese fondue",
        "bread baking", "risotto recipe", "frying pan", "vegan recipes", "cake", "espresso machine", "salad",
        "gift ideas", "christmas cookies", "tea", "barbecue", "soup"]],
    "mcp.outdoorithm.com": [("search_gear", {"query": q, "limit": 5}) for q in [
        "tent", "sleeping bag", "hiking boots", "camp stove", "headlamp", "backpack", "sleeping pad", "water filter",
        "rain jacket", "trekking poles", "cooler", "camp chair", "lantern", "hammock", "first aid kit",
        "cookware", "down jacket", "bear canister", "camp table", "kids sleeping bag"]],
    "mcp.supplementenscanner.nl": [("search_products", {"query": q, "limit": 5}) for q in [
        "creatine", "vitamine d", "magnesium", "omega 3", "whey proteine", "ashwagandha", "zink", "vitamine c",
        "collageen", "melatonine", "ijzer", "b12", "multivitamine", "probiotica", "l-theanine", "kurkuma",
        "q10", "foliumzuur", "elektrolyten", "glucosamine"]],
    "moltad.net":
        [("search_tiktok_products", {"query": q, "limit": 5}) for q in [
            "lip gloss", "phone case", "hoodie", "skincare", "water bottle", "sneakers", "air fryer", "led lights",
            "hair dryer", "protein powder", "backpack", "earbuds"]] +
        [("search_affiliate_offers", {"q": q, "limit": 5}) for q in [
            "mattress", "software", "vpn", "travel", "fashion", "fitness", "hosting", "pet"]],
    "padel.how":
        [("search_rackets", {"query": q, "limit": 5}) for q in [
            "bullpadel", "adidas", "head", "nox", "babolat", "siux", "control", "power", "beginner", "carbon"]] +
        [("get_offers", {"slug": s, "limit": 5}) for s in [
            "adidas-arrow-hit-2026-review", "adidas-arrow-hit-ctrl-2026-review", "adidas-cross-it-ctrl-2026-review",
            "adidas-cross-it-light-2026-review", "adidas-metalbone-2026-review", "bullpadel-hack-04-comfort-2026",
            "bullpadel-vertex-05-geo-2026-review", "bullpadel-hack-04-hybrid-2026", "bullpadel-neuron-02-2026",
            "bullpadel-pearl-2026-review"]],
    "picoads.xyz": [("get_recommendations", {"topic": t, "context": c, "max_results": 5}) for t, c in [
        ("defi-yield", "where can I earn yield on USDC"), ("defi-yield", "safest staking options"),
        ("agent-tools", "tools for building AI agents"), ("agent-tools", "hosting for an MCP server"),
        ("crypto-tax-portfolio-tracking", "how do I file crypto taxes"), ("crypto-tax-portfolio-tracking", "portfolio tracker app"),
        ("jobs", "remote software engineering jobs"), ("jobs", "how to find a data science job"),
        ("travel-deals", "cheap flights to tokyo"), ("travel-deals", "hotel deals in lisbon"),
        ("productivity-tools", "best note taking app"), ("productivity-tools", "project management for small teams"),
        ("saas-deals", "discount on design software"), ("saas-deals", "cheap CRM for startups"),
        ("e-commerce", "start an online store"), ("e-commerce", "dropshipping suppliers"),
        ("finance-banking", "best high yield savings account"), ("finance-banking", "business bank account"),
        ("education-learning", "learn python online"), ("health-wellness", "meditation app")]],
    "piqod.it": [("search_experiences", {"query": q, "limit": 5}) for q in [
        "cosa fare a Roma", "biglietti per il Colosseo", "tour in barca a Capri", "Musei Vaticani", "Uffizi Firenze",
        "gondola Venezia", "Cinque Terre tour", "degustazione vini Chianti", "Pompei escursione", "Lago di Como battello",
        "Torre di Pisa", "corso di cucina Bologna", "Costiera Amalfitana", "Milano Cenacolo", "Napoli street food",
        "Etna escursione", "Verona Arena", "Dolomiti trekking", "Sicilia tour", "Roma di notte"]],
    "qubitsok.com": [("searchJobs", {"query": q, "limit": 5}) for q in [
        "quantum software engineer", "error correction", "photonics", "product manager", "postdoc quantum",
        "cryogenic engineer", "quantum algorithms researcher", "ion trap", "superconducting qubits", "remote quantum job",
        "quantum machine learning", "FPGA engineer quantum", "quantum sensing", "internship quantum",
        "quantum chemistry", "control systems engineer", "quantum networking", "sales quantum computing",
        "quantum jobs in Germany", "quantum hardware engineer"]],
    "stackswap.ai":
        [("recommend_partner", {"category": c}) for c in [
            "outbound", "CRM", "automation", "email", "analytics", "enrichment", "data", "scheduling", "support",
            "marketing", "sales engagement", "intent data", "website", "AI SDR", "reporting"]] +
        [("search_tools", {"query": q, "limit": 5}) for q in ["hubspot", "apollo", "clay", "salesforce", "zapier"]],
    "umesh-malik.com": [("get_post", {"slug": s}) for s in [
        "how-to-build-mcp-server", "deploy-mcp-server-cloudflare-workers", "make-your-site-agent-readable",
        "secure-mcp-write-tools-writeguard", "optional-oauth-scopes-mcp-servers", "claude-code-macos-printer-driver",
        "reduce-s3-storage-costs", "reactive-dom-javascript-proxy", "typescript-utility-types-complete-guide",
        "javascript-es2024-features-you-should-know", "nodejs-backend-for-frontend-developers",
        "shadow-dom-innerhtml-not-working", "claude-opus-5-guide", "chatgpt-apps-sdk-super-app-guide",
        "plugin-registry-security-architecture", "use-claude-code-codex-for-free",
        "postgres-storage-bottleneck-local-nvme-benchmark", "streaming-html-out-of-order-without-javascript",
        "gemini-agent-hooks-fail-open", "mcp-write-controls-cloudflare-writeguard"]],
    "voyagehacks.com":
        [("search_travel_gear", {"query": q, "limit": 5}) for q in [
            "carry-on backpack", "packing cubes", "travel adapter", "power bank", "noise cancelling headphones",
            "travel pillow", "rfid wallet", "toiletry bag"]] +
        [("get_esim_links", {"destination": d}) for d in ["Japan", "Thailand", "USA", "Turkey", "Portugal", "Mexico"]] +
        [("get_car_rental_links", {"destination": d}) for d in ["Crete", "Georgia", "Bali", "Sicily", "Montenegro", "Iceland"]],
    "wem3.ai":
        [("search_products", {"query": q, "limit": 5}) for q in [
            "iphone 16", "sony headphones", "dyson vacuum", "nintendo switch", "kindle paperwhite", "lego star wars",
            "air fryer", "garmin watch", "ipad", "nespresso"]] +
        [("find_lowest_price", {"query": q}) for q in [
            "airpods pro", "samsung galaxy s25", "logitech mx master", "ps5", "instant pot", "gopro",
            "bose soundbar", "philips hue", "jbl speaker", "ssd 2tb"]],
    "www.choov.de": [("get_tariffs", {"category": c, "plz": p}) for c in ["energy", "gas", "insurance", "creditcard", "telecom"]
                     for p in ["10115", "80331", "20095", "50667"]],
    "www.coinrebate.vip": [("get_exchange_fees", {})],
    "www.gigstamp.co.uk": [("search_gigs_and_events", {"city": city, "query": q, "limit": 5})
                           for city in ["oxford", "brighton"] for q in [
                               "jazz", "rock", "comedy", "open mic", "folk", "tribute band", "classical", "indie",
                               "blues", "festival"]],
    "www.peanutbutterjelly.io": [("search_deals", a) for a in [
        {"query": q} for q in ["bitcoin", "ethereum", "low fees", "sign up bonus", "staking", "ledger", "trezor",
                               "cold wallet", "futures", "beginner", "usa", "europe", "kyc", "savings", "card"]] + [
        {"query": "exchange", "category": "exchange"}, {"query": "wallet", "category": "hardware_wallet"},
        {"query": "bonus", "category": "exchange"}, {"query": "secure", "category": "hardware_wallet"},
        {"query": "trading", "category": "exchange"}]],
    "tulugar.com": [("search_listings", {"city": c, "listing_type": lt, "property_type": pt, "limit": 5})
                    for c, lt, pt in [
                        ("Asunción", "sale", "apartment"), ("Asunción", "rent", "apartment"), ("Asunción", "sale", "house"),
                        ("Asunción", "rent", "house"), ("Asunción", "sale", "land"), ("Asunción", "sale", "commercial"),
                        ("Luque", "sale", "house"), ("San Lorenzo", "sale", "house"), ("Lambaré", "sale", "apartment"),
                        ("Encarnación", "sale", "apartment"), ("Encarnación", "rent", "house"), ("Ciudad del Este", "sale", "apartment"),
                        ("Ciudad del Este", "rent", "apartment"), ("Fernando de la Mora", "sale", "house"), ("Mariano Roque Alonso", "sale", "land"),
                        ("Asunción", "rent", "commercial"), ("Luque", "rent", "apartment"), ("San Bernardino", "sale", "house"),
                        ("Capiatá", "sale", "land"), ("Villa Elisa", "sale", "house")]],
    "bluesky.caseyjhand.com": [("bsky_search_actors", {"query": q, "limit": 5}) for q in [
        "wireless headphones", "tech deals", "amazon finds", "gadget reviews", "home office setup", "running shoes",
        "coffee gear", "camera gear", "skincare routine", "budget travel", "gaming setup", "kitchen gadgets",
        "smart home", "fitness equipment", "book recommendations", "mechanical keyboards", "outdoor gear",
        "fashion deals", "baby products", "pet supplies"]],
    "socialbridge-mcp.vercel.app": [("search_all", {"q": q, "platforms": "youtube", "limit": 5}) for q in [
        "wireless headphones", "best budget phone", "robot vacuum review", "air fryer review", "best running shoes",
        "mechanical keyboard", "espresso machine", "4k monitor", "standing desk", "best laptop for students",
        "smartwatch review", "camping gear", "electric toothbrush", "gaming mouse", "portable charger",
        "best vpn", "skincare routine", "bluetooth speaker", "home gym", "travel backpack"]],
    # unavailable live (kept so the reason is explicit)
    "deal.ly": [],
    "mcp.nomadstays.com": [],
}
for h, qs in WO.items():
    Q[h] = [("search_offers", {"query": q, "limit": 5}) for q in qs]

NOTES = {
    "www.coinrebate.vip": "tool takes no arguments: 1 distinct input x 20 time-separated calls",
    "cashbackpro.org": "get_promo_codes takes no arguments: 1 of 20 slots",
    "mcp-production-680d.up.railway.app": "only 5 category values exist: 5 categories x 4 result limits",
}


def main():
    prov = list(csv.DictReader(open(PROV)))
    ad_tools = collections.defaultdict(set)
    tcat = {}
    for r in prov:
        ad_tools[r["server"]].add(r["tool"])
        tcat[(r["server"], r["tool"])] = r["tool_category"]
    for h, (_ep, cat, _o) in EXTRA.items():
        ad_tools[h].add(EXTRA_TOOLS[h])
        tcat[(h, EXTRA_TOOLS[h])] = cat
    live = {}
    for line in open(TL):
        d = json.loads(line)
        live[d["host"]] = (d["endpoint"], {t["name"] for t in d.get("tools") or []})
    assert set(Q) == set(ad_tools), set(Q) ^ set(ad_tools)

    rng = random.Random(SEED)
    plan, unavailable = [], {}
    for host in sorted(Q):
        ep, live_tools = live[host]
        inputs = [(t, a) for t, a in Q[host] if t in ad_tools[host] and t in live_tools]
        bad = [t for t, _ in Q[host] if t not in ad_tools[host]]
        assert not bad, (host, bad)
        missing = sorted(ad_tools[host] - live_tools)
        if not inputs:
            unavailable[host] = {"endpoint": ep, "confirmed_ad_tools": sorted(ad_tools[host]),
                                 "reason": "endpoint returns HTTP 404" if not live_tools
                                 else f"ad tool(s) no longer listed: {missing}"}
            continue
        reps = 20 if host == "www.coinrebate.vip" else REPS
        if host != "www.coinrebate.vip":
            assert len(inputs) == 20, (host, len(inputs))
        for rep in range(reps):
            order = list(range(len(inputs)))
            rng.shuffle(order)
            for qi in order:
                t, a = inputs[qi]
                plan.append({"host": host, "endpoint": ep, "tool": t, "tool_category": tcat[(host, t)],
                             "arguments": a, "query_id": f"{host}#q{qi:02d}", "rep": rep,
                             "note": NOTES.get(host)})
    json.dump(plan, open(HERE / "plan_meta.json", "w"), indent=0, ensure_ascii=False)
    json.dump(unavailable, open(HERE / "plan_meta_unavailable.json", "w"), indent=1)
    by = collections.Counter(p["host"] for p in plan)
    print(f"servers planned: {len(by)} | calls: {len(plan)} | unavailable: {sorted(unavailable)}")
    print("calls/server:", sorted(set(by.values())))


if __name__ == "__main__":
    main()
