# healthyagingatlas.com

- **Endpoint:** https://healthyagingatlas.com/api/mcp
- **Server:** healthy-aging-atlas 2.0.0
- **Ad-serving tool(s):** search_supplements
- **Tool category:** shopping
- **Distinct ads observed:** 10 | **ad impressions:** 90
- **Coder confidence / basis:** high / source_code
- **Server instructions:** Use the evidence tools for clinical evidence, citations, and dataset questions. Evidence tools are educational, source-linked, and commerce-free. Use the legacy commerce tools only when the user explicitly asks for products, prices, or purchase options; disclose affiliate links. Never present an evidence grade, product score, or dataset count as personalized medical advice.

## Evidence (why coded as advertising)
- *tool `search_supplements`* — affiliate_url field with Amazon tag; description: results may contain affiliate URLs

## Example advertised items / links
- `www.amazon.com/dp/B0019GW3G8?tag=healthagingat-20`  (impressions: 13)
- `www.amazon.com/dp/B000NRXNOK?tag=healthagingat-20`  (impressions: 13)
- `www.amazon.com/dp/B00L9TK484?tag=healthagingat-20`  (impressions: 13)
- `www.amazon.com/dp/B000BD0RT0?tag=healthagingat-20`  (impressions: 13)
- `www.amazon.com/dp/B000BD0RQS?tag=healthagingat-20`  (impressions: 13)
- `www.amazon.com/dp/B08YS9T41V?tag=healthagingat-20`  (impressions: 6)
- `www.amazon.com/dp/B0013OUNK4?tag=healthagingat-20`  (impressions: 6)
- `www.amazon.com/dp/B002N4TF6M?tag=healthagingat-20`  (impressions: 6)
- `www.amazon.com/dp/B0013HV8RI?tag=healthagingat-20`  (impressions: 6)
- `www.amazon.com/dp/B01JAAVHLQ?tag=healthagingat-20`  (impressions: 1)

## All tools exposed by this server
### `search_evidence`
Search published HAA supplement-goal evidence records. Returns evidence grades, mapped study counts, limitations, review dates, and clean canonical HAA sources. Contains no affiliate links or purchase recommendations. Use only for public, non-personal evidence questions. Do not call this tool for requests involving personal or sensitive health information, including medical records, medication lists, diagnoses, symptoms, laboratory results, or treatment planning. Tell the user not to submit that information and direct them to a qualified healthcare professional.

### `get_evidence_summary`
Return one source-accurate, citable HAA summary for a supplement-goal pair, including evidence boundary, limitations, safety flags, reviewer metadata, and a clean canonical source. Contains no affiliate links. Use only for public, non-personal evidence questions. Do not call this tool for requests involving personal or sensitive health information, including medical records, medication lists, diagnoses, symptoms, laboratory results, or treatment planning. Tell the user not to submit that information and direct them to a qualified healthcare professional.

### `get_citations`
Return only PubMed-cache-verified citations that pass the repository source-accuracy audit for a published supplement-goal record. Mismatched, conflicting, or unverifiable citations are counted and withheld. Stored claim prose is never emitted without claim-level verification. Contains no affiliate links. Use only for public, non-personal evidence questions. Do not call this tool for requests involving personal or sensitive health information, including medical records, medication lists, diagnoses, symptoms, laboratory results, or treatment planning. Tell the user not to submit that information and direct them to a qualified healthcare professional.

### `query_evidence_map`
Query the DOI-backed HAA Supplement Evidence Density Map 2026. Returns dataset version, denominator, methods, canonical citation, and filtered rows from the published CSV. Contains no affiliate links. Use only for public, non-personal evidence questions. Do not call this tool for requests involving personal or sensitive health information, including medical records, medication lists, diagnoses, symptoms, laboratory results, or treatment planning. Tell the user not to submit that information and direct them to a qualified healthcare professional.

### `compare_evidence`
Compare mapped human-evidence strength and limitations for two to five supplements for the same goal. This is an evidence comparison, not a product ranking or purchase recommendation, and contains no affiliate links. Use only for public, non-personal evidence questions. Do not call this tool for requests involving personal or sensitive health information, including medical records, medication lists, diagnoses, symptoms, laboratory results, or treatment planning. Tell the user not to submit that information and direct them to a qualified healthcare professional.

### `search_supplements`
Legacy commerce tool. Search catalog products by name, ingredient, or brand. Results may contain affiliate URLs; use search_evidence for commerce-free clinical evidence.

### `get_product`
Legacy commerce tool. Retrieve product-quality, certification, price, availability, and affiliate purchase data. Use get_evidence_summary for clinical evidence.

### `compare_supplements`
Legacy comparison tool that may include catalog and affiliate data. Use compare_evidence for a commerce-free evidence comparison.

### `get_price_history`
Legacy commerce tool. Retrieve retailer price observations and freshness; contains no clinical efficacy conclusion.

### `recommend_for_goal`
Legacy commerce tool. Returns catalog/product rankings and may contain affiliate URLs. Rankings are not clinical-evidence grades or personalized advice.
