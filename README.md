# Who Pays the Agent? — MCP discovery crawler and ad study

This repository does two things:

1. **Discovery crawl.** Collect every remote MCP server listed in public MCP
   directories and download what each server publishes about itself: tool names,
   descriptions and input/output schemas; resources; prompts (including their
   full text); and server instructions. **It never calls a tool.**
2. **Ad study.** Find MCP servers that carry paid content (sponsored results,
   affiliate links, ad networks for AI agents), observe the ads with a small
   number of read-only tool calls, and test whether AI models tell users that an
   item is paid.

```
.
├── run_pipeline.sh          # one command: directories -> merged pool -> discovery
├── discover.py              # the MCP discovery scanner (Part A)
├── mcp_paths.py             # helper: which data/<date>/ folder the analysis scripts read
├── requirements.txt
├── inputs/                  # original Glama-derived endpoint list (2026-09-30)
├── directories/             # Part A: directory collectors
│   ├── collect.py           #   enumerate one directory -> directories/raw/<source>.jsonl
│   └── merge.py             #   merge + dedupe -> directories/endpoints.csv
├── analysis/                # Part B1, B4, C: analysis scripts, codebook, labels
└── ad_probe/                # Part B2-B3: opt-in read-only tool-call probe
```

Generated data (`data/`, `directories/raw/`, `directories/endpoints.csv`,
`analysis/out/`, `ad_probe/results/`) is **not** in git. Re-create it with the
commands below.

---

## 0. Setup (one time)

You need Python 3.10 or newer (`python3 --version`).

```bash
git clone git@github.com:pooryousefshahrooz/mcp-discovery-crawler.git
cd mcp-discovery-crawler
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Part A — Discovery crawl

### A1. Quick test (20 servers, about 1 minute)

```bash
python3 discover.py --limit 20
```

### A2. Full pipeline (one command)

```bash
./run_pipeline.sh
```

It runs three steps. Each is **resumable**: if anything stops (Ctrl-C, crash,
lost Wi-Fi), run the same command again and it continues where it stopped.

| Step | Command | What it does | Time |
|---|---|---|---|
| 1 | `python3 directories/collect.py --source X` | enumerate one directory (all five run in parallel) | hours (Glama, MCP.so) |
| 2 | `python3 directories/merge.py` | merge and de-duplicate endpoints into `directories/endpoints.csv`, and print a per-directory table | seconds |
| 3 | `python3 discover.py` | discovery on the **whole pool**: `directories/endpoints.csv` plus `inputs/*.csv`, de-duplicated | hours |

To re-scan servers without re-collecting the directories:
`./run_pipeline.sh --skip-collect`.

**Directories and how they are read** (as checked on 2026-09-30):

| Source | Mechanism | Notes |
|---|---|---|
| Official MCP Registry | public JSON API (`/v0/servers`, cursor paging) | complete |
| Smithery | public sitemap + list API searches + per-server detail API | the list API caps every query at 500, and the sitemap repeats the same 5,000 URLs on every page, so only about 9,500 of about 17,800 servers can be reached |
| Glama | public sitemap (`mcp-remote-servers/*.xml`) + listing pages | the JSON API needs a key; its license requires visible attribution to Glama |
| MCP.so | public sitemap + listing pages | `/api/` is disallowed by robots.txt and is not used |
| MCP Directory | public sitemap + listing pages | `/api/` is disallowed by robots.txt and is not used |
| PulseMCP | — | **not collected**: the API needs an `X-API-Key`, and the website is behind a Cloudflare challenge. If you get a key, ask before adding it. |

### A3. What discovery sends (and never sends)

For each endpoint, `discover.py` sends only:

1. `initialize` and `notifications/initialized`
2. `tools/list`, following pagination
3. `resources/list` and `prompts/list`, if the server advertises them
4. `prompts/get` for each prompt, to store its full text (turn off with `--no-prompt-contents`)

It **never sends `tools/call`**. Every outgoing message is checked against
`ALLOWED_METHODS`, and anything else is refused. **Do not change this.**

Useful options:

| Option | Default | Meaning |
|---|---|---|
| `--input A.csv B.csv` | the whole pool | one or more CSVs with an `endpoint` column |
| `--limit N` | all | only the first N endpoints (for testing) |
| `--concurrency N` | 10 | servers contacted at the same time. Please don't raise this much. |
| `--timeout S` | 20 | seconds per request |
| `--date YYYY-MM-DD` | today | output subfolder; use it to resume a run that crossed midnight |
| `--no-prompt-contents` | off | list prompts, but don't fetch their text |

### A4. Output (`data/<date>/`)

- `<host>__<hash>.json`: one file per server, written as soon as that server finishes.
  - `status`: one of `ok`, `auth_required` (401/403; we never log in), `initialize_failed`, `tools_list_failed`, `network_error`, or `crawler_error`.
  - `server_info`, `server_protocol_version`, `server_capabilities`.
  - `exchanges`: the **raw** HTTP exchanges (request, status, headers, untouched body, parsed response).
  - `summary`: counts of tools, resources and prompts.
- `prompts/<host>__<hash>.json`: full prompt texts. Required arguments are filled with placeholders such as `<topic>`. When a server rejects a placeholder and lists the allowed values, the request is retried once with the first allowed value.
- `_index.jsonl`: one line per server, for quick counts:

```bash
python3 -c "import json,collections;print(collections.Counter(json.loads(l)['status'] for l in open('data/2026-09-30/_index.jsonl')))"
```

Only Streamable HTTP (POST to the endpoint) is supported; SSE-only servers show
up as `initialize_failed`.

---

## Part B — Ad study

All analysis scripts read the **newest** `data/<date>/` folder. To use another
crawl, set `MCP_DATA_DIR`, e.g.:

```bash
MCP_DATA_DIR=data/2026-09-30 python3 analysis/ads_scan.py
```

### B1. Which servers declare paid content (offline, no network)

```bash
python3 analysis/ads_scan.py          # candidates from metadata  -> analysis/out/ads_candidates.jsonl
python3 analysis/ads_misses.py        # second pass (sponsors, routing users elsewhere)
python3 analysis/build_coding_sheet.py # blind coding sheet -> analysis/coding_sheet.csv
```

The detectors only produce **candidates**: many hits are unrelated (ad-management
tools, "CPC" meaning patent class, clinical-trial "sponsor"). Every candidate is
labeled **by hand** using `analysis/ads_codebook.md`. The labels are in:

- `analysis/ads_labels_full.json`: final labels for the whole corpus
- `analysis/ads_labels_adjudicated.json`: first corpus, after second coding

After a **new crawl**, label only the servers not coded before:

```bash
python3 analysis/build_coding_sheet.py --name coding_sheet_new3 --prefix P \
    --exclude out/coding_sheet.jsonl out/coding_sheet_new.jsonl out/coding_sheet_new2.jsonl
```

**TODO for you (second coder):** open `analysis/coding_sheet.csv` (and the
`_new` / `_new2` sheets) **without** looking at our labels. Fill the `code`
column using the codebook, then run:

```bash
python3 analysis/ads_agreement.py --csv analysis/coding_sheet.csv
```

It reports percent agreement and Cohen's κ, and lists the disagreements to
discuss.

Other offline analyses:

- `analysis/ads_angles.py`: branding pushed into replies, upsell, tracking parameters, lead capture, clone clusters
- `analysis/ads_where.py`: where in the metadata the ad signals sit, ad networks named, repeated ad text
- `analysis/rq45_scan.py`, `analysis/rq4_classes.py`: instruction-like content in tool metadata and prompts

### B2. Observe served ads (opt-in, calls tools on third-party servers)

> **Read this first.** Unlike Part A, this step **calls tools** on other
> people's servers, so the rules below are not optional:
> - only free, read-only search/list/recommend tools
> - **never** billing, checkout, sign-up, booking, payment, or x402-priced tools
> - **never** tools that return data about identifiable people or accounts
> - never follow or click any link in a result (clicks cost advertisers money)
> - stop a server at its first HTTP 429; keep at least 2.5 s between calls
> - check with the supervisor before every new probe run

```bash
python3 ad_probe/build_plan.py         # plan for servers labeled as carrying ads -> ad_probe/plan_v2.json
python3 ad_probe/build_wide_plan.py    # plan for all other servers (1 call per host) -> ad_probe/plan_wide.json
```

**Review the plan JSON by hand before running it.** Remove any tool that could
change state, cost money, or return personal data. Then run:

```bash
python3 ad_probe/probe_ads_v2.py <run-label> plan_v2.json
python3 ad_probe/probe_ads_v2.py <run-label>-wide plan_wide.json
```

The runner refuses any call that is not literally in the plan. Results go to
`ad_probe/results/v2/<run-label>/<host>.jsonl`.

### B3. Detect and verify ads in the results

```bash
python3 ad_probe/detect_ads.py "ad_probe/results/v2/<run-label>/*.jsonl"
```

It prints per-server and overall rates (paid placements, affiliate links, click
trackers) and writes `ad_probe/results/detections.csv`.

**Every hit must be verified by hand.** In our wide probe, 6 of 8 automatic hits
were false positives: a job-ad URL, an image path, a directory describing
another server, an explicit "no affiliate links" statement, a "no paid
placement" statement, and third-party web page content.

`ad_probe/extract_ads.py` builds a per-ad catalog from the older round-1/2
results of `probe_ads.py`.

### B4. Do AI models pass the ad label on? (offline, local models)

```bash
python3 analysis/ad_replay.py
```

It replays recorded ad-bearing tool results to local models through
[Ollama](https://ollama.com) (`ollama pull llama3.2:3b mistral:7b phi4:14b qwen2.5:32b`).
**It is CPU/GPU heavy**, so run it overnight. It is resumable and writes
`analysis/out/ad_replay.jsonl`. Its scores come from keyword patterns:
**manually check a random sample of answers before reporting any number.**

---

## Safety summary

| Step | Contacts third-party servers? | Calls tools? |
|---|---|---|
| Part A (collect, merge, discover) | yes, discovery only | **no** |
| B1, B3, B4 | no | no |
| B2 (ad probe) | yes | **yes**, read-only and pre-reviewed plan only |
