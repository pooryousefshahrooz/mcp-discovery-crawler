# MCP discovery crawler (`before_the_call/`)

`discover.py` connects to every MCP server listed in
`inputs/mcp_servers_online_live_2026-09-30.csv` and asks each one what it offers.
It **only runs discovery**:

1. `initialize`
2. `notifications/initialized`
3. `tools/list`
4. `resources/list`, only if the server says it supports resources
5. `prompts/list`, only if the server says it supports prompts
6. `prompts/get` for each listed prompt, to save the full prompt text. This is
   read-only. Turn it off with `--no-prompt-contents`.

It **never sends `tools/call`**. The script refuses to send any method that is
not on the list above (see `ALLOWED_METHODS` in `discover.py`). **Do not change
this.** Calling a tool on someone else's server can have real side effects.

## 1. Setup (one time)

You need Python 3.10 or newer. Check your version with `python3 --version`.

```bash
cd before_the_call
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Test run (20 servers)

```bash
cd before_the_call
source .venv/bin/activate
python3 discover.py --limit 20
```

Each server prints one line when it finishes, for example:

```
[1/20] ok                tools=4    res=0    prompts=0    https://402oracle.com/mcp
```

## 3. Full run (all ~6,200 servers)

```bash
python3 discover.py
```

If the run stops (Ctrl-C, crash, lost Wi-Fi), **run the same command again**.
Servers that already have a result file for today are skipped.

Options:

| Option | Default | Meaning |
|---|---|---|
| `--limit N` | all | only the first N rows of the CSV (for testing) |
| `--concurrency N` | 10 | number of servers contacted at the same time. Please don't raise this much. |
| `--timeout S` | 20 | seconds to wait for each request |
| `--input PATH` | `inputs/mcp_servers_online_live_2026-09-30.csv` | a different endpoint list |
| `--outdir PATH` | `data/` | results go to `<outdir>/<date>/` |
| `--no-prompt-contents` | off | only list prompts; don't fetch their text with `prompts/get` |
| `--date YYYY-MM-DD` | today | output subfolder name; use it to resume a run that crossed midnight |

## 4. Output

Results go into `data/<today's date>/`, for example `data/2026-09-30/`:

- **`<host>__<hash>.json`**: one file per server, written as soon as that server
  finishes. It contains:
  - `endpoint`, `input_row` (the original CSV row), `started_at`, `finished_at`
  - `status`: one of
    - `ok`: `tools/list` succeeded
    - `auth_required`: the server answered 401/403 (needs a login or API key; we do not log in)
    - `initialize_failed`: the server answered, but not with a valid MCP `initialize` result
    - `tools_list_failed`: `initialize` worked, but `tools/list` returned an error
    - `network_error`: DNS, TLS, connection or timeout failure
    - `crawler_error`: the whole server took longer than 8 × timeout, or the script hit a bug
  - `server_info`, `server_protocol_version`, `server_capabilities` (from `initialize`)
  - `exchanges`: the **raw data**. There is one entry per HTTP request, with the
    JSON-RPC `request` we sent, `http_status`, response `headers`, the untouched
    `raw_body` (JSON or SSE text), the parsed JSON-RPC `response`, and `elapsed_s`.
  - `summary`: counts of tools, resources and prompts (for convenience only; the
    real data is in `exchanges`)
- **`prompts/<host>__<hash>.json`**: the full text of every prompt, for servers
  that list prompts. It contains:
  - `exchanges`: one raw `prompts/get` request and response per prompt. The
    prompt text is in `response.result.messages`.
  - `n_fetched`: how many prompts returned their text.
  - Required arguments are filled with visible placeholders such as
    `<project_description>`, so you can see where user input goes.
  - If a server rejects a placeholder and its error message lists the allowed
    values, the request is retried once with the first allowed value. That
    retry is marked `retry_of_invalid_arguments`.
  - Servers crawled before prompt fetching existed are **backfilled**
    automatically on the next run, using a short new session (`initialize`,
    then `prompts/get`).
- **`_index.jsonl`**: one line per finished server (status and counts), for a
  quick overview:

```bash
# how many servers ended in each status
python3 -c "import json,collections;print(collections.Counter(json.loads(l)['status'] for l in open('data/2026-09-30/_index.jsonl')))"
```

Notes:
- Each day's run gets its own folder, and resuming only skips servers already in
  **that** folder. If a run crosses midnight, resume it with
  `python3 discover.py --date 2026-09-30` (the date the run started).
- Only Streamable HTTP (a POST to the endpoint URL) is supported. Old
  SSE-only servers will show up as `initialize_failed`.
