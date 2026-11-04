# RQ3 — Query-conditioned ad targeting in MCP servers

**Question.** Does the same MCP server return *different advertisements* depending on
the user's query?

## Method
For every eligible server (an ad-signal host that exposes a free-text query/search
tool), we call that one tool with **four distinct in-domain queries × 10 repeats**,
interleaved and randomised to remove temporal/ordering bias; all non-query arguments
are held constant. From each response we extract the set of **advertisement
identities** (explicit `[Sponsored]`/`is_promoted` items + affiliate-network links;
tracking-only UTM links and ordinary commercial content are *not* counted). We then
compute, per server:

- **within-query** Jaccard — ad-set similarity across repeats of the *same* query;
- **across-query** Jaccard — ad-set similarity across *different* queries;
- **targeting gap** = within − across (positive ⇒ query-dependent ad selection).

Aggregates use a hierarchical bootstrap (resample servers, then repeats). `qubitsok`
is reported separately as a fixed house-promotion baseline (within = across = 1.0,
gap = 0).

## Pipeline (code lives in `../../ad_probe/`)
1. `rq3_build_plan.py` → `rq3_targeting_plan.json` (eligible servers + query param + safe base args)
2. `rq3_domain_queries.json` — per-server, four in-domain queries
3. `rq3_run.py --mode domain --reps 10 --gap 2.5` — live, read-only probe (never follows links; stops a host on HTTP 429)
4. `rq3_analyze.py --indir rq3_domain --tag _domain` — metrics + figure

## Files here
- `fig_query_targeting_domain.pdf/.png` — paired dot plot (main figure)
- `rq3_metrics_domain.csv` — per-server within/across/gap + per-query ad frequency
- `rq3_ads_domain.csv` — extracted ad identities per (server, query, repeat)

## Headline result
Among servers that serve a confirmed ad through a query tool, ad delivery is
**deterministic and query-conditioned**: within-query Jaccard = 1.00, across-query
≈ 0.11, **mean targeting gap ≈ 0.89 (95% CI [0.70, 1.00])** over five servers.
A focused repeat (same query ×10) returned the identical paid item 10/10; a load
test (100 calls over 25 queries) returned a sponsored item on 100% of calls (two
per response, ≈20% of listed items).

**Note.** Raw per-endpoint responses and probe outputs are intentionally *not*
committed (size + possible third-party session ids/tokens); regenerate with the
pipeline above.
