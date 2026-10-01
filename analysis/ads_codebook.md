# Codebook: paid influence in MCP server metadata

**Unit:** one MCP server (endpoint).
**Evidence:** only what is in the coding sheet: server instructions, tool
descriptions, and schema field names from discovery. Do not look anything up.

**Question:** does this server put *paid or commercial influence from which
it or a partner earns money* into the AI agent's context, aimed at the end
user? Give exactly one code, using the **first** rule that applies.

| Code | Use when | Not this code when |
|---|---|---|
| `AD_NETWORK` | The server itself sells, brokers or serves ad placements to agents or MCP publishers, or pays for traffic it attributes | It only *analyzes* ads or manages ad campaigns for a customer (→ `NONE`) |
| `SPONSORED_CONTENT_NETWORK` | The server presents itself as editorial or informational, a sponsor is named, and the agent is told to route users to that sponsor | The sponsor is only a data field, e.g. a clinical-trial sponsor (→ `NONE`) |
| `COMPETITOR_SUPPRESSION` | The agent is told not to name competitors and/or to steer every user to the operator | The server only prefers its own tools over its own other tools (→ `NONE`) |
| `AGENT_PAID_TO_RECOMMEND` | The agent or its operator is offered money (commission, kickback, tokens) for recommending or referring | Referral codes that only give the *user* a discount (→ `AFFILIATE`) |
| `SPONSORED_RESULTS` | Tool results can contain sponsored, promoted, featured-for-pay or plan-ranked items, or a required ad slot | "featured" with no sign of payment (→ `NONE`) |
| `AFFILIATE` | Links or codes in results earn the operator a commission or referral fee, or the agent is told to keep tracked links intact | Referral-code *inputs* for the user's own account signup with no commission to the operator (→ `NONE`) |
| `NEUTRALITY_CLAIM` | The server explicitly says there is **no** paid placement, sponsorship or affiliate bias, and nothing above applies | |
| `NONE` | Anything else: ad-tech SaaS for customers, CPC/CPA/CPM as data (patents, accountants, critical path), SEC "disclosure", trial "sponsor", the server's own pricing or upsell | |

**Tie-breaks:**
- If several codes apply, take the first matching row in the table order.
- If the evidence is ambiguous, code `NONE` and add a note.
