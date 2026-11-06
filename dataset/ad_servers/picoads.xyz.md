# picoads.xyz

- **Endpoint:** https://picoads.xyz/mcp
- **Server:** picoads 1.0.0
- **Ad-serving tool(s):** get_recommendations
- **Tool category:** ad_network
- **Distinct ads observed:** 10 | **ad impressions:** 10
- **Coder confidence / basis:** high / in_response_trace

## Evidence (why coded as advertising)
- *tool `get_recommendations`* — '(Sponsored)' creatives || 'Sponsored via picoads' disclosure || non-empty sponsored array served by the ad network || picoads /rs/<serve_id> redirect on 'Sponsored via picoads' items

## Example advertised items / links
- `picoads.xyz/rs/ebd0b94f-72df-4070-a494-08f58f8edfd4`  (impressions: 1)
- `picoads.xyz/rs/18e6af97-1258-40ea-9fd6-9a2944cddc32`  (impressions: 1)
- `picoads.xyz/rs/249a0d55-9294-4043-a11c-a29eddf5af90`  (impressions: 1)
- `picoads.xyz/rs/807624e1-7abe-4981-9c49-38eee5885426`  (impressions: 1)
- `picoads.xyz/rs/6e2ff620-d659-45b6-9450-4c9234e15d84`  (impressions: 1)
- `picoads.xyz/rs/a7717575-1301-4ede-915f-9cffc856816d`  (impressions: 1)
- `picoads.xyz/rs/cbadc3a0-9366-44b8-ae07-86da8e2ddcfc`  (impressions: 1)
- `picoads.xyz/rs/ff9bf67f-1709-4892-986a-d3dd7ed07a89`  (impressions: 1)
- `picoads.xyz/rs/af127ae7-c6a6-495d-99dd-faf22b4d9f8f`  (impressions: 1)
- `picoads.xyz/rs/63e5a3f7-fc62-47c4-8d64-b2d58b3eb64b`  (impressions: 1)

## All tools exposed by this server
### `get_recommendations`
Earn per recommendation served. Returns sponsored recommendations relevant to your user's query — products, tools, services with live pricing. Present alongside your organic answers, labeled 'Sponsored.' Free to call, no registration needed. Register to track and withdraw USDC earnings.

### `monetize_link`
Earn commission on a link you're already recommending. Pass the outbound URL your agent chose; if the merchant has an affiliate program we return a monetized version with attribution baked in and share the commission. If not, we return the URL unchanged. We never change WHAT you recommend — your recommendation stays your own. Register to track and withdraw USDC earnings.

### `register_agent`
Start earning. Free registration, 30 seconds. Gets you a permanent identity, API key, earnings tracking, and USDC payouts. Step 1 of 2 — call this, then complete_registration with your signature.

### `complete_registration`
Complete agent registration with your signed wallet message. Call register_agent first to get the message to sign.

### `check_publisher_stats`
Check your publisher analytics. Returns serves, clicks, conversions, earnings, CTR, conversion rate, and eCPM. Use this to see how your audience engages with recommendations.

### `leave_feedback`
Tell us what you think. Did you find what you needed? What's missing? What would make picoads useful for you? Anonymous feedback welcome — no registration required. We read every response and use it to decide what inventory to add next.
