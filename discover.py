#!/usr/bin/env python3
"""MCP discovery-only crawler.

For each endpoint in the input CSV, speaks MCP over Streamable HTTP and sends
ONLY discovery requests:

    initialize -> notifications/initialized -> tools/list
    -> resources/list  (only if the server advertises the `resources` capability)
    -> prompts/list    (only if the server advertises the `prompts` capability)
    -> prompts/get     (once per listed prompt, to store the full prompt text;
                        disable with --no-prompt-contents)

It NEVER sends tools/call (or any other method): every outgoing message is
checked against ALLOWED_METHODS before it is sent.

Each server's raw HTTP exchanges are written to data/<YYYY-MM-DD>/<id>.json as
soon as that server finishes, so an interrupted run can simply be restarted
and it will skip servers that already have a result file. Full prompt texts go
to data/<YYYY-MM-DD>/prompts/<id>.json; servers that were crawled before their
prompt texts were fetched are backfilled on the next run.
"""

import argparse
import asyncio
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
# Default pool = every directory endpoint (directories/endpoints.csv, built by
# directories/collect.py + merge.py) plus the original Glama-derived input list.
DEFAULT_INPUTS = [HERE / "directories" / "endpoints.csv",
                  HERE / "inputs" / "mcp_servers_online_live_2026-09-30.csv"]
DEFAULT_OUTDIR = HERE / "data"

CLIENT_PROTOCOL_VERSION = "2025-06-18"
CLIENT_INFO = {"name": "mcp-discovery-measurement", "version": "1.0"}
USER_AGENT = "mcp-discovery-measurement/1.0 (academic research; discovery only, no tool calls)"

# The only JSON-RPC methods this script is allowed to send.
ALLOWED_METHODS = {
    "initialize",
    "notifications/initialized",
    "tools/list",
    "resources/list",
    "prompts/list",
    "prompts/get",   # read-only: returns a prompt template's messages
}

MAX_PAGES = 20                   # cap on nextCursor pagination per list method
MAX_BODY_BYTES = 5 * 1024 * 1024  # truncate stored raw bodies beyond this
MAX_PROMPT_GETS = 100            # cap on prompts/get requests per server


def server_id(endpoint: str) -> str:
    """Stable, filesystem-safe file name for an endpoint."""
    host = re.sub(r"^https?://", "", endpoint).split("/")[0]
    host = re.sub(r"[^A-Za-z0-9.-]", "_", host)[:80]
    digest = hashlib.sha1(endpoint.encode()).hexdigest()[:10]
    return f"{host}__{digest}"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_sse(text: str) -> list:
    """Return the JSON payloads of all `data:` events in an SSE body."""
    messages, data_lines = [], []
    for line in text.splitlines() + [""]:
        if line.startswith("data:"):
            data_lines.append(line[5:].lstrip())
        elif line == "" and data_lines:
            payload = "\n".join(data_lines)
            data_lines = []
            try:
                messages.append(json.loads(payload))
            except json.JSONDecodeError:
                pass
    return messages


class Session:
    def __init__(self, client: httpx.AsyncClient, endpoint: str, timeout: float):
        self.client = client
        self.endpoint = endpoint
        self.timeout = timeout
        self.session_id = None
        self.protocol_version = None
        self.next_id = 1

    def _headers(self) -> dict:
        h = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": USER_AGENT,
        }
        if self.session_id:
            h["Mcp-Session-Id"] = self.session_id
        if self.protocol_version:
            h["MCP-Protocol-Version"] = self.protocol_version
        return h

    async def send(self, method: str, params=None, notification=False) -> dict:
        """Send one JSON-RPC message; return a record of the raw exchange."""
        if method not in ALLOWED_METHODS:
            raise RuntimeError(f"refusing to send non-discovery method {method!r}")

        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        req_id = None
        if not notification:
            req_id = self.next_id
            self.next_id += 1
            msg["id"] = req_id

        rec = {"method": method, "request": msg, "sent_at": now_iso()}
        t0 = time.monotonic()
        try:
            async with self.client.stream(
                "POST", self.endpoint, json=msg, headers=self._headers(),
                timeout=self.timeout,
            ) as resp:
                rec["http_status"] = resp.status_code
                rec["http_version"] = resp.http_version
                rec["final_url"] = str(resp.url)
                rec["headers"] = dict(resp.headers)
                ctype = resp.headers.get("content-type", "")
                body, truncated, response = b"", False, None

                if "text/event-stream" in ctype and not notification:
                    # SSE streams may stay open after the reply; stop reading
                    # once the message matching our request id has arrived.
                    async for chunk in resp.aiter_bytes():
                        body += chunk
                        for m in parse_sse(body.decode("utf-8", "replace")):
                            if isinstance(m, dict) and m.get("id") == req_id and (
                                "result" in m or "error" in m
                            ):
                                response = m
                        if response is not None or len(body) > MAX_BODY_BYTES:
                            break
                else:
                    async for chunk in resp.aiter_bytes():
                        body += chunk
                        if len(body) > MAX_BODY_BYTES:
                            truncated = True
                            break

                if len(body) > MAX_BODY_BYTES:
                    body, truncated = body[:MAX_BODY_BYTES], True
                text = body.decode("utf-8", "replace")
                rec["raw_body"] = text
                rec["body_truncated"] = truncated

                if response is None and not notification:
                    if "text/event-stream" in ctype:
                        msgs = parse_sse(text)
                    else:
                        try:
                            parsed = json.loads(text) if text.strip() else None
                        except json.JSONDecodeError:
                            parsed = None
                        msgs = parsed if isinstance(parsed, list) else [parsed]
                    for m in msgs:
                        if isinstance(m, dict) and m.get("id") == req_id:
                            response = m
                rec["response"] = response
        except Exception as e:  # network errors, timeouts, TLS failures, ...
            rec["error"] = f"{type(e).__name__}: {e}"
        rec["elapsed_s"] = round(time.monotonic() - t0, 3)
        return rec


async def list_all(sess: Session, method: str, exchanges: list):
    """Call a */list method, following nextCursor pagination."""
    cursor = None
    for _ in range(MAX_PAGES):
        params = {"cursor": cursor} if cursor else {}
        rec = await sess.send(method, params)
        exchanges.append(rec)
        result = (rec.get("response") or {}).get("result")
        if not isinstance(result, dict):
            return
        cursor = result.get("nextCursor")
        if not cursor:
            return


async def open_session(sess: Session, exchanges: list):
    """initialize + notifications/initialized; returns the initialize result or None."""
    init = await sess.send("initialize", {
        "protocolVersion": CLIENT_PROTOCOL_VERSION,
        "capabilities": {},
        "clientInfo": CLIENT_INFO,
    })
    exchanges.append(init)
    result = (init.get("response") or {}).get("result")
    if not isinstance(result, dict):
        return None
    sess.session_id = init["headers"].get("mcp-session-id")
    sess.protocol_version = result.get("protocolVersion")
    exchanges.append(await sess.send("notifications/initialized", notification=True))
    return result


def listed_items(exchanges: list, method: str, key: str) -> list:
    items = []
    for ex in exchanges:
        if ex["method"] == method:
            r = (ex.get("response") or {}).get("result") or {}
            if isinstance(r, dict) and isinstance(r.get(key), list):
                items += r[key]
    return items


def placeholder_arguments(prompt: dict) -> dict:
    """Fill each required argument with a visible placeholder like <name>, so
    the stored text shows where user input lands in the template."""
    args = {}
    for a in prompt.get("arguments") or []:
        if isinstance(a, dict) and a.get("required") and a.get("name"):
            args[a["name"]] = f"<{a['name']}>"
    return args


def allowed_values_from_error(error: dict) -> dict:
    """From an 'invalid arguments' error (-32602), pull {arg: first allowed value}
    when the server's validator lists the allowed values (zod-style issues)."""
    error = error or {}
    msg = error.get("message") or ""
    start = msg.find("[")
    if error.get("code") != -32602 or start < 0:
        return {}
    try:
        issues = json.loads(msg[start:])
    except json.JSONDecodeError:
        return {}
    fixes = {}
    for i in issues if isinstance(issues, list) else []:
        path, values = i.get("path"), i.get("values") or i.get("options")
        if isinstance(path, list) and len(path) == 1 and isinstance(values, list) and values:
            fixes[str(path[0])] = str(values[0])
    return fixes


async def get_prompts(sess: Session, prompts: list) -> dict:
    """prompts/get for each listed prompt; returns the prompts-file content."""
    out = {"arguments_policy": "required arguments filled with '<name>' placeholders; "
                               "on a -32602 error listing allowed values, retried once "
                               "with the first allowed value",
           "exchanges": []}
    seen = set()
    for p in prompts:
        name = p.get("name") if isinstance(p, dict) else None
        if not name or name in seen:
            continue
        seen.add(name)
        if len(seen) > MAX_PROMPT_GETS:
            out["capped_at"] = MAX_PROMPT_GETS
            break
        # Always send `arguments` (some servers reject a missing object).
        args = placeholder_arguments(p)
        rec = await sess.send("prompts/get", {"name": name, "arguments": args})
        out["exchanges"].append(rec)
        fixes = allowed_values_from_error((rec.get("response") or {}).get("error"))
        if fixes:
            rec = await sess.send("prompts/get",
                                  {"name": name, "arguments": {**args, **fixes}})
            rec["retry_of_invalid_arguments"] = True
            out["exchanges"].append(rec)
    out["n_fetched"] = len({
        ex["request"]["params"]["name"] for ex in out["exchanges"]
        if isinstance((ex.get("response") or {}).get("result"), dict)})
    return out


async def backfill_prompts(client: httpx.AsyncClient, res: dict, timeout: float) -> dict:
    """New short session for a server crawled before prompt texts were fetched."""
    sess = Session(client, res["endpoint"], timeout)
    session_exchanges = []
    if await open_session(sess, session_exchanges) is None:
        return {"status": "initialize_failed", "session_exchanges": session_exchanges}
    out = await get_prompts(sess, listed_items(res["exchanges"], "prompts/list", "prompts"))
    out["session_exchanges"] = session_exchanges
    out["status"] = "ok"
    return out


async def discover(client: httpx.AsyncClient, row: dict, timeout: float,
                   fetch_prompts: bool = True) -> tuple:
    endpoint = row["endpoint"]
    out = {
        "endpoint": endpoint,
        "input_row": row,
        "started_at": now_iso(),
        "client_protocol_version": CLIENT_PROTOCOL_VERSION,
        "exchanges": [],
    }
    sess = Session(client, endpoint, timeout)
    prompts_out = None

    result = await open_session(sess, out["exchanges"])
    init = out["exchanges"][0]

    if result is None:
        if "error" in init:
            out["status"] = "network_error"
        elif init.get("http_status") in (401, 403):
            out["status"] = "auth_required"
        else:
            out["status"] = "initialize_failed"
    else:
        caps = result.get("capabilities") or {}
        out["server_info"] = result.get("serverInfo")
        out["server_protocol_version"] = sess.protocol_version
        out["server_capabilities"] = caps

        # tools/list is always attempted; the other lists only when advertised.
        await list_all(sess, "tools/list", out["exchanges"])
        tools_ok = any(ex["method"] == "tools/list"
                       and isinstance((ex.get("response") or {}).get("result"), dict)
                       for ex in out["exchanges"])
        if "resources" in caps:
            await list_all(sess, "resources/list", out["exchanges"])
        if "prompts" in caps:
            await list_all(sess, "prompts/list", out["exchanges"])
            prompts = listed_items(out["exchanges"], "prompts/list", "prompts")
            if fetch_prompts and prompts:
                # Own deadline, so a slow prompts phase can't lose the lists above.
                try:
                    prompts_out = await asyncio.wait_for(
                        get_prompts(sess, prompts), timeout=timeout * 8)
                    prompts_out["status"] = "ok"
                except Exception as e:
                    prompts_out = {"status": "crawler_error",
                                   "error": f"{type(e).__name__}: {e}"}
        out["status"] = "ok" if tools_ok else "tools_list_failed"

    # Convenience summary; the raw data is in `exchanges`.
    out["summary"] = {
        "n_tools": len(listed_items(out["exchanges"], "tools/list", "tools")),
        "n_resources": len(listed_items(out["exchanges"], "resources/list", "resources")),
        "n_prompts": len(listed_items(out["exchanges"], "prompts/list", "prompts")),
    }
    out["finished_at"] = now_iso()
    return out, prompts_out


def wrap_prompts(res: dict, prompts_out: dict) -> dict:
    return {"endpoint": res["endpoint"], "server_info": res.get("server_info"),
            "fetched_at": now_iso(), **prompts_out}


def write_atomic(path: Path, obj: dict):
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


async def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, nargs="+", default=None,
                    help="one or more CSV files with an `endpoint` column "
                         "(default: directories/endpoints.csv + inputs/*.csv, whichever exist)")
    ap.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR,
                    help="results go to OUTDIR/<date>/ (default: data/)")
    ap.add_argument("--limit", type=int, default=None,
                    help="only process the first N endpoints of the CSV (for testing)")
    ap.add_argument("--concurrency", type=int, default=10)
    ap.add_argument("--date", default=dt.date.today().isoformat(),
                    help="name of the output subfolder (default: today, YYYY-MM-DD); "
                         "pass an earlier date to resume a run that crossed midnight")
    ap.add_argument("--timeout", type=float, default=20.0,
                    help="per-request timeout in seconds")
    ap.add_argument("--no-prompt-contents", dest="fetch_prompts", action="store_false",
                    help="skip prompts/get (only list prompts, don't fetch their text)")
    args = ap.parse_args()

    inputs = args.input or [p for p in DEFAULT_INPUTS if p.exists()]
    rows, seen = [], set()
    for path in inputs:
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                ep = (r.get("endpoint") or "").strip()
                key = ep.rstrip("/").lower()
                if ep.startswith("http") and key not in seen:
                    seen.add(key)
                    r["input_file"] = path.name
                    rows.append(r)
    print("input files:", ", ".join(str(p) for p in inputs), flush=True)
    if args.limit is not None:
        rows = rows[: args.limit]

    day_dir = args.outdir / args.date
    day_dir.mkdir(parents=True, exist_ok=True)
    index_path = day_dir / "_index.jsonl"
    prompts_dir = day_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)

    todo = [r for r in rows if not (day_dir / f"{server_id(r['endpoint'])}.json").exists()]
    print(f"{len(rows)} endpoints selected, {len(rows) - len(todo)} already done, "
          f"{len(todo)} to run -> {day_dir}", flush=True)

    # Already-crawled servers that list prompts but have no prompts file yet.
    backfill = []
    if args.fetch_prompts:
        for r in rows:
            sid = server_id(r["endpoint"])
            path = day_dir / f"{sid}.json"
            if path.exists() and not (prompts_dir / f"{sid}.json").exists():
                res = json.loads(path.read_text())
                if res.get("summary", {}).get("n_prompts", 0) > 0:
                    backfill.append(res)
        if backfill:
            print(f"{len(backfill)} already-crawled servers need prompt texts (backfill)",
                  flush=True)

    sem = asyncio.Semaphore(args.concurrency)
    done = 0
    limits = httpx.Limits(max_connections=args.concurrency * 2)

    async with httpx.AsyncClient(follow_redirects=True, limits=limits,
                                 timeout=args.timeout) as client:
        async def worker(row):
            nonlocal done
            async with sem:
                prompts_out = None
                try:
                    # discover() gives its prompts/get phase a separate deadline.
                    res, prompts_out = await asyncio.wait_for(
                        discover(client, row, args.timeout, args.fetch_prompts),
                        timeout=args.timeout * 17)
                except Exception as e:  # hard per-server deadline or bug
                    res = {"endpoint": row["endpoint"], "input_row": row,
                           "status": "crawler_error",
                           "error": f"{type(e).__name__}: {e}",
                           "finished_at": now_iso()}
            sid = server_id(row["endpoint"])
            # Prompts file first: the main file marks the server as done.
            if prompts_out is not None:
                write_atomic(prompts_dir / f"{sid}.json", wrap_prompts(res, prompts_out))
            write_atomic(day_dir / f"{sid}.json", res)
            line = {"id": sid, "endpoint": row["endpoint"], "status": res["status"],
                    **res.get("summary", {}), "finished_at": res["finished_at"]}
            with open(index_path, "a") as f:
                f.write(json.dumps(line) + "\n")
                f.flush()
            done += 1
            s = res.get("summary", {})
            print(f"[{done}/{len(todo)}] {res['status']:<17} "
                  f"tools={s.get('n_tools', '-'):<4} res={s.get('n_resources', '-'):<4} "
                  f"prompts={s.get('n_prompts', '-'):<4}"
                  + (f"(texts={prompts_out.get('n_fetched', 0)}) " if prompts_out else " ")
                  + row["endpoint"], flush=True)

        backfilled = 0

        async def backfill_worker(res):
            nonlocal backfilled
            async with sem:
                try:
                    out = await asyncio.wait_for(
                        backfill_prompts(client, res, args.timeout),
                        timeout=args.timeout * 9)
                except Exception as e:
                    out = {"status": "crawler_error", "error": f"{type(e).__name__}: {e}"}
            sid = server_id(res["endpoint"])
            write_atomic(prompts_dir / f"{sid}.json", wrap_prompts(res, out))
            backfilled += 1
            print(f"[backfill {backfilled}/{len(backfill)}] {out['status']:<17} "
                  f"prompts={res['summary']['n_prompts']} texts={out.get('n_fetched', 0)} "
                  f"{res['endpoint']}", flush=True)

        await asyncio.gather(*(worker(r) for r in todo),
                             *(backfill_worker(r) for r in backfill))

    print("done.", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit("interrupted; rerun the same command to resume.")
