#!/usr/bin/env python3
"""RQ4/RQ5: instruction-like content in MCP discovery metadata and prompt templates.

Reads a snapshot of data/<date>/ (safe while discover.py is still running:
only complete *.json files are read) and extracts every text surface a model
sees during discovery:

  RQ4  server_instructions  initialize.result.instructions
       tool_name / tool_title / tool_description
       param_description    any `description` inside a tool's inputSchema
  RQ5  prompt_description / prompt_arg_description   (prompts/list)
       prompt_message       text of each message returned by prompts/get

Each surface is run through regex detectors (candidates only; every hit still
needs manual review). Writes:
  out/surfaces_flagged.jsonl   one line per surface with >= 1 detector hit
  out/prompt_messages.jsonl    every prompts/get message (for RQ5 structure)
  out/summary.json             counts per surface / detector
"""

import argparse
import collections
import glob
import json
import re
import unicodedata
from pathlib import Path
import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from mcp_paths import data_dir  # noqa: E402

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- detectors
I = re.I
DETECTORS = {
    # obfuscation: text a human reviewer would not see
    "invisible_unicode": None,  # handled in code (see invisible_chars)
    "html_comment": re.compile(r"<!--.*?-->", re.S),
    "hidden_tag": re.compile(
        r"<\s*/?\s*(important|system|instructions?|secret|hidden|admin|override|"
        r"assistant|sys|priority|critical)\b[^>]*>|\[(system|admin|important)\]", I),
    # classic injection phrasing
    "override": re.compile(
        r"\b(ignore|disregard|forget|override)\b[^.\n]{0,40}\b(previous|prior|above|"
        r"earlier|other|all|any|system|existing)\b[^.\n]{0,20}\b(instructions?|prompts?|"
        r"rules?|guidelines?|directions?)\b|\bnew instructions\b|\byou are now\b", I),
    "secrecy": re.compile(
        r"\b(do not|don't|never|must not|without)\s+(tell(ing)?|inform(ing)?|mention(ing)?|"
        r"reveal(ing)?|show(ing)?|disclos(e|ing)|notify(ing)?|alert(ing)?|let(ting)?|"
        r"ask(ing)?)\b[^.\n]{0,30}\b(the )?user\b|\bsilently\b|\bkeep (this|it) "
        r"(secret|hidden|confidential)\b|\bthe user (must|should) not (know|see)\b", I),
    # steering the agent's tool choice (shadowing / preference manipulation)
    "tool_steering": re.compile(
        r"\bbefore (using|calling|invoking|running) (any|other|another|all)\b|"
        r"\binstead of (using |calling )?(any |the )?(other|another|built-?in|native|"
        r"default|web ?search|browser|\w+ tool)\b|"
        r"\b(do not|don't|never) (use|call|invoke) (any )?(other|another|different|"
        r"alternative|competing|built-?in|web)\b|"
        r"\b(always|only) (use|call|prefer|choose|pick) (this|these|our)\b|"
        r"\b(prefer|preferred|prioriti[sz]e)\b[^.\n]{0,30}\b(over|above) (any|all|other)\b|"
        r"\bfor (all|any|every) (requests?|queries|questions|tasks)\b", I),
    "must_call_first": re.compile(
        r"\b(always|must|required to|first)\b[^.\n]{0,25}\b(call|invoke|use|run)\b"
        r"[^.\n]{0,40}\b(first|before)\b|\bALWAYS call\b", I),
    # data exfiltration / sensitive material
    "sensitive_data": re.compile(
        r"~/\.ssh|\bid_rsa\b|\.env\b|\bmcp\.json\b|claude_desktop_config|"
        r"\bprivate key\b|\bseed phrase\b|\bmnemonic\b|\bsystem prompt\b|"
        r"\b(conversation|chat) history\b|\bentire (conversation|context|chat)\b|"
        r"\b(previous|prior|all) messages\b|\bpasswords?\b|\bcredentials?\b|"
        r"\bapi[_ -]?keys?\b|\bsecrets?\b", I),
    "exfil_verbs": re.compile(
        r"\b(send|forward|upload|post|transmit|include|pass|append|attach)\b[^.\n]{0,40}"
        r"\b(conversation|chat history|system prompt|previous messages|context window|"
        r"all (messages|files|data)|user'?s? (data|files|messages|credentials)|"
        r"environment variables|file contents)\b", I),
    # role / persona manipulation
    "persona": re.compile(
        r"(^|[.!\n]\s*)(you are (a|an|the)\b|act as\b|your (role|job|task) is\b|"
        r"as an ai\b|as the assistant\b)", I),
    # urgency / coercion markers (weak signal, used for ranking only)
    "coercive_caps": re.compile(r"\b(IMPORTANT|CRITICAL|MANDATORY|MUST|NEVER|ALWAYS|"
                                r"REQUIRED|WARNING)\b"),
}
WEAK = {"coercive_caps", "sensitive_data"}   # informative alone, not a flag

INVISIBLE_RANGES = [
    (0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x2064), (0x2066, 0x2069),
    (0xFEFF, 0xFEFF), (0x00AD, 0x00AD), (0x180E, 0x180E),
    (0xE0000, 0xE007F),  # Unicode tag characters ("ASCII smuggling")
    (0xE0100, 0xE01EF),  # variation selectors supplement
]


def invisible_chars(text):
    out = []
    for ch in text:
        cp = ord(ch)
        if any(a <= cp <= b for a, b in INVISIBLE_RANGES):
            out.append(f"U+{cp:04X}")
    return out


def decode_tags(text):
    """Decode Unicode tag characters (U+E0020..E007E) back to ASCII."""
    return "".join(chr(ord(c) - 0xE0000) for c in text if 0xE0020 <= ord(c) <= 0xE007E)


def run_detectors(text):
    hits = {}
    inv = invisible_chars(text)
    if inv:
        hits["invisible_unicode"] = sorted(set(inv))
        tag = decode_tags(text)
        if tag:
            hits["decoded_tag_text"] = tag
    for name, rx in DETECTORS.items():
        if rx is None:
            continue
        found = [m.group(0) for m in rx.finditer(text)]
        if found:
            hits[name] = found[:10]
    return hits


# ------------------------------------------------------------ extraction
def schema_descriptions(schema, path="$"):
    """Yield (json_path, description) for every description in a JSON schema."""
    if isinstance(schema, dict):
        for k, v in schema.items():
            if k == "description" and isinstance(v, str) and path != "$":
                yield path, v
            elif isinstance(v, (dict, list)):
                yield from schema_descriptions(v, f"{path}.{k}")
    elif isinstance(schema, list):
        for i, v in enumerate(schema):
            yield from schema_descriptions(v, f"{path}[{i}]")


def results(d, method):
    for ex in d.get("exchanges", []):
        if ex.get("method") == method:
            r = (ex.get("response") or {}).get("result")
            if isinstance(r, dict):
                yield ex, r


def surfaces_for_server(d):
    ep = d["endpoint"]
    for _, r in results(d, "initialize"):
        if isinstance(r.get("instructions"), str) and r["instructions"].strip():
            yield ep, "server_instructions", None, r["instructions"]
    for _, r in results(d, "tools/list"):
        for t in r.get("tools") or []:
            if not isinstance(t, dict):
                continue
            name = str(t.get("name", ""))
            yield ep, "tool_name", name, name
            if isinstance(t.get("title"), str):
                yield ep, "tool_title", name, t["title"]
            if isinstance(t.get("description"), str):
                yield ep, "tool_description", name, t["description"]
            for p, desc in schema_descriptions(t.get("inputSchema") or {}):
                yield ep, "param_description", f"{name}:{p}", desc
    for _, r in results(d, "prompts/list"):
        for p in r.get("prompts") or []:
            if not isinstance(p, dict):
                continue
            if isinstance(p.get("description"), str):
                yield ep, "prompt_description", p.get("name"), p["description"]
            for a in p.get("arguments") or []:
                if isinstance(a, dict) and isinstance(a.get("description"), str):
                    yield ep, "prompt_arg_description", f"{p.get('name')}:{a.get('name')}", a["description"]


def message_text(content):
    if not isinstance(content, dict):
        return None
    if content.get("type") == "text":
        return content.get("text")
    if content.get("type") == "resource":
        res = content.get("resource") or {}
        return res.get("text")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=HERE / "out")
    args = ap.parse_args()
    args.data = args.data or data_dir()
    args.out.mkdir(exist_ok=True)

    files = sorted(glob.glob(str(args.data / "*.json")))
    counts = collections.Counter()           # surfaces per type
    hitc = collections.defaultdict(collections.Counter)   # detector -> surface -> n
    hit_servers = collections.defaultdict(set)
    n_servers = n_ok = 0
    flagged = open(args.out / "surfaces_flagged.jsonl", "w")

    def handle(ep, surface, where, text):
        counts[surface] += 1
        text = unicodedata.normalize("NFC", text)
        h = run_detectors(text)
        strong = [k for k in h if k not in WEAK and k != "decoded_tag_text"]
        for k in h:
            hitc[k][surface] += 1
        for k in strong:
            hit_servers[k].add(ep)
        if strong:
            flagged.write(json.dumps({"endpoint": ep, "surface": surface, "where": where,
                                      "len": len(text), "hits": h, "text": text},
                                     ensure_ascii=False) + "\n")

    for f in files:
        try:
            d = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue  # being written right now
        n_servers += 1
        if d.get("status") != "ok":
            continue
        n_ok += 1
        for ep, surface, where, text in surfaces_for_server(d):
            handle(ep, surface, where, text)

    # RQ5: prompts/get messages
    pm = open(args.out / "prompt_messages.jsonl", "w")
    prompt_stats = collections.Counter()
    for f in sorted(glob.glob(str(args.data / "prompts" / "*.json"))):
        try:
            d = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        prompt_stats["servers"] += 1
        for ex in d.get("exchanges", []):
            params = ex["request"].get("params", {})
            r = (ex.get("response") or {}).get("result")
            if not isinstance(r, dict):
                continue
            prompt_stats["prompts_fetched"] += 1
            for i, m in enumerate(r.get("messages") or []):
                c = m.get("content")
                text = message_text(c)
                rec = {"endpoint": d["endpoint"], "prompt": params.get("name"),
                       "arguments": params.get("arguments"), "idx": i,
                       "role": m.get("role"),
                       "ctype": c.get("type") if isinstance(c, dict) else None,
                       "text": text}
                pm.write(json.dumps(rec, ensure_ascii=False) + "\n")
                prompt_stats[f"role:{m.get('role')}"] += 1
                if text:
                    handle(d["endpoint"], "prompt_message",
                           f"{params.get('name')}#{i}:{m.get('role')}", text)

    summary = {
        "servers_read": n_servers, "servers_ok": n_ok,
        "surfaces": dict(counts),
        "detector_hits_by_surface": {k: dict(v) for k, v in hitc.items()},
        "servers_with_strong_hit": {k: len(v) for k, v in hit_servers.items()},
        "servers_with_any_strong_hit": len(set().union(*hit_servers.values())) if hit_servers else 0,
        "prompt_stats": dict(prompt_stats),
    }
    json.dump(summary, open(args.out / "summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
