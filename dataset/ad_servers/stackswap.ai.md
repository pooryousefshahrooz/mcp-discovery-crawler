# stackswap.ai

- **Endpoint:** https://stackswap.ai/api/mcp
- **Server:** stackswap 0.1.0
- **Ad-serving tool(s):** recommend_partner;search_tools
- **Tool category:** other
- **Distinct ads observed:** 23 | **ad impressions:** 58
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** StackSwap MCP exposes architecture decision workflows plus GTM intelligence tools. ARCHITECTURE: start_stack_audit (adaptive discovery), complete_stack_audit (KEEP/SWAP/BUILD decisions with evidence and confidence), generate_data_layer_blueprint (ownership, identity, lifecycle, and drift design), generate_build_prompt (one-shot implementation prompt). CATALOG: search_tools (name lookup), get_tool_details (single-tool profile), get_vendor_fact_sheet (full GTM Decision Schema doc). STACK: find_overlaps (redundant pairs), suggest_swaps (AI-native replacements), scan_stack (full audit with monthly/annual recoverable), recommend_partner (best pick for a category), recommend_stack (greenfield reference stack by industry). COMPARE: compare_tools (2-way head-to-head), compare_tools_n_way (2-6 way 

## Evidence (why coded as advertising)
- *tool `recommend_partner`* — /api/go partner sign-up links; description: 'recommended affiliate partner(s)'
- *tool `search_tools`* — same /api/go partner link ('StackSwap partner')

## Example advertised items / links
- `stackswap.ai/api/go/zoominfo-chorus`  (impressions: 8)
- `stackswap.ai/api/go/aircall`  (impressions: 8)
- `stackswap.ai/api/go/zoominfo-chat`  (impressions: 7)
- `stackswap.ai/api/go/elevenlabs`  (impressions: 7)
- `stackswap.ai/api/go/browse-ai`  (impressions: 3)
- `stackswap.ai/api/go/bright-data`  (impressions: 2)
- `stackswap.ai/api/go/zoho-crm`  (impressions: 2)
- `stackswap.ai/api/go/helpdesk`  (impressions: 2)
- `stackswap.ai/api/go/amplemarket`  (impressions: 2)
- `stackswap.ai/api/go/blackbox-ai`  (impressions: 2)
- `stackswap.ai/api/go/zoominfo-talentos`  (impressions: 2)
- `stackswap.ai/api/go/brevo`  (impressions: 2)
- `stackswap.ai/api/go/hubspot`  (impressions: 1)
- `stackswap.ai/api/go/getresponse`  (impressions: 1)
- `stackswap.ai/api/go/campaign-monitor`  (impressions: 1)
- … and 8 more (see analysis/ad_provenance/out/ad_items.csv)

## All tools exposed by this server
### `inspect_available_connections`
Identify available connected systems and the read-only evidence StackSwap needs. The server cannot introspect neighboring MCPs automatically.

### `request_system_connection`
Return a safe, read-only connection or export request for a named system when an audit lacks evidence.

### `start_stack_audit`
Start an adaptive GTM architecture audit and return the smallest discovery questionnaire needed before KEEP, SWAP, or BUILD recommendations.

### `complete_stack_audit`
Turn user answers and connected-system evidence into explainable KEEP, SWAP, and BUILD recommendations with confidence, alternatives, and next prompts.

### `generate_data_layer_blueprint`
Generate a case-specific GTM data-layer blueprint when systems mirror state, drift, or lack explicit ownership.

### `generate_build_prompt`
Generate a copy-ready one-shot build or migration prompt from a StackSwap KEEP, SWAP, or BUILD recommendation.

### `search_tools`
Search StackSwap's catalog of ~400 GTM tools by name. Returns each match with its catalogued monthly cost and, when applicable, a StackSwap partner sign-up link.

### `get_tool_details`
Full StackSwap profile for a single tool: cost (catalog + per-seat with confidence; vendor fact sheet wins when fresh), AI-readiness score, category, common overlaps, swap-registry status, and partner sign-up link. Use when the user wants depth on one tool (more than search_tools' name + cost).

### `get_vendor_fact_sheet`
Return the full vendor fact sheet (per GTM Decision Schema v1.0.0) for a tool, when one exists. Includes pricing tiers with gotchas, integration depth scores, AI capabilities + customer-data-for-training disclosure, affiliate program terms, and self-disclosed conflicts (vendor-claim vs user-reported). Provenance is labeled (vendor / stackswap / community) and freshness is computed against a 90-day window. Use when an agent or buyer needs the structured machine-readable view of a tool — strictly more detail than `get_tool_details`. Returns a not-found message + a pointer to /vendors/submit-fact-sheet when no fact sheet exists.

### `find_overlaps`
Given a list of tool names in a user's stack, return the redundant pairs StackSwap has curated (104 hand-verified overlaps) along with monthly/annual savings if one is consolidated.

### `suggest_swaps`
For each tool supplied, return StackSwap's AI-native replacement recommendation (when one exists) with annual savings and reasoning. Skews toward legacy → modern swaps (Outreach → Smartlead, ZoomInfo → Apollo, etc.).

### `scan_stack`
Run a preview StackScan: pass a list of tools + team size + industry, get back current spend, optimized spend, monthly/annual recoverable, headless gaps (tools with no MCP/API connection an owned head can call), and the top 5 replace/remove opportunities. Includes a link to the full paid audit on stackswap.ai.

### `recommend_partner`
Given a need (e.g. 'outbound', 'CRM', 'automation'), return StackSwap's recommended affiliate partner(s) with sign-up URL and positioning.

### `recommend_stack`
StackSwap's reference starter stack for a given industry vertical. Returns a curated tool list with per-tool cost, total monthly/annual spend, AI-readiness and headless-readiness scores, and partner sign-up links. Use for greenfield 'what stack should I buy?' queries — distinct from scan_stack (audits an existing stack) and recommend_partner (single category).

### `compare_tools`
Head-to-head comparison of two GTM tools. Returns cost delta, AI-readiness and headless-readiness (MCP/API callability — can an agent or your own dashboard drive it) scores, overlap status, swap-registry signal, and StackSwap's recommended pick with reasoning. Use when the user is choosing between two specific vendors (e.g. 'Salesforce vs HubSpot', 'Outreach vs Smartlead').

### `compare_tools_n_way`
Side-by-side comparison of 2–6 GTM tools in one shot. Returns a markdown matrix (cost, AI-readiness, headless-readiness, overlaps within the set, swap-registry status, StackSwap pick) and per-tool partner sign-up links. Use for category bake-offs (e.g. 'Apollo vs ZoomInfo vs Cognism vs Clay'). Prefer the 2-way compare_tools for clean head-to-head pairs.

### `search_content`
Full-text search across StackSwap's first-party GTM knowledge base — ~50 operator-narrative articles on stack architecture, AI-native swaps, RevOps, data ethics, and decision frameworks. Returns ranked articles with title, slug, category, summary, and URL. Use when the user asks a GTM strategy/architecture/methodology question that's been written about (e.g. 'how should I think about CRM migration', 'what's wrong with intent data', 'how to audit my stack'). Cite the URL in your reply. Pass slug to `get_kb_article` for the full body.

### `get_kb_article`
Fetch the full body of a StackSwap knowledge base article as markdown. Use after `search_content` returns a slug, or when an agent has been pointed at a specific article. Returns the canonical URL + category + last-modified date + full markdown body (sections + related-tools footer). Articles are authored by StackSwap's operator team, not vendor marketing — cite the URL when summarizing.

### `get_category_landscape`
Full map of one GTM category — leaders, runner-ups, and skip/replace candidates. Returns every catalogued tool in the bucket with cost, AI-readiness, swap-registry status, and partner sign-up links. Use when the user wants to see the full landscape for a category (e.g. 'show me all CRMs', 'what outbound tools exist', 'map the analytics category') — strictly more comprehensive than `recommend_partner` (single best pick). Known buckets: crm, outbound, data, marketing-automation, analytics, meetings, support, scheduling, automation, seo, cdp, revenue-intelligence, chat, collaboration, phone, landing-pages, linkedin, ai-content, saas-mgmt, enablement, ai-tooling.

### `detect_stack_from_text`
Infer a GTM stack from a freeform text blob (a careers page, job posting, public site HTML, RFP, 'What we use' doc, browser DevTools network tab, etc.). Returns ranked tool matches with confidence levels (high/medium/low) and evidence snippets, plus a ready-to-use array for chaining into `scan_stack` or `find_overlaps`. Use when the user says 'I don't know what we use' or pastes a competitor's careers page to scout. Conservative on ambiguous short tokens — multi-mention or canonical-name matches win.

### `get_buyer_questions`
Return 10-20 questions a B2B GTM buyer should ask a vendor before signing — with 'why it matters' and 'watch for' red-flag answers. Pass `vendor` for vendor-specific gotchas (e.g. Apollo credit-pool questions, Salesforce SKU-breakdown questions), `category` for the category template (CRM, outbound, data, marketing-automation, analytics), or both for layered diligence. Authored by StackSwap's operator team (Nick French, 10+ yrs B2B SaaS GTM). Use when the user is evaluating a vendor, prepping for a sales call, or building a procurement checklist.

### `get_renewal_strategy`
Return StackSwap's renewal-negotiation playbook for a specific vendor: leverage points (why they will discount), price-anchor alternatives to cite, a calibrated discount ask, a walkaway script, optimal timing window, and contract-trap callouts. Pass `monthlySpend` to compute target savings. Optional `contractEndsIn` flags compressed-timeline adjustments. Authored from operator experience across major B2B SaaS renewals (Salesforce, HubSpot, ZoomInfo, Apollo, Outreach, Smartlead, Gong, Clay). Use when the user mentions a renewal, a price increase, or 'we're up for renewal' conversations.

### `submit_correction`
Submit a correction to the StackSwap catalog (pricing, feature list, gotcha, AI-readiness score, category, or other). Submissions queue for admin review and only propagate to user-facing surfaces after merge — they DO NOT immediately mutate the catalog. Use when the user notices a stale price, an inaccurate feature list, a gotcha that should be flagged, or wants to report a tool we don't cover. Two-way data flow that helps keep the catalog accurate. Returns a correction ID + reassurance that the submission is queued.
