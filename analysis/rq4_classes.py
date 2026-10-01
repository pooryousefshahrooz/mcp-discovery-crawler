"""Refined, higher-precision RQ4/RQ5 classes, applied to ALL surfaces (not only
first-pass hits). Writes out/class_hits.jsonl; manual review happens on top."""
import json, re, glob, collections, sys
from pathlib import Path
import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from mcp_paths import data_dir  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from rq45_scan import surfaces_for_server, message_text
I = re.I
CLASSES = {
 # server claims the agent's attention beyond its own tools
 "scope_grab": re.compile(
   r"\binstead of (a |the |using |doing )?(web ?search(es)?|search(ing)? the web|browsing|"
   r"google|your (own )?(knowledge|training|memory)|training data|other (tools|sources|servers|mcp))\b|"
   r"\b(do not|don't|never)\s+(answer|respond|rely)\b[^.\n]{0,25}\b(from|on|using)\s+(your )?"
   r"(training|memory|own knowledge|general knowledge|prior knowledge)\b|"
   r"\b(do not|don't|never)\s+(use|call|invoke)\s+(any\s+)?(other|another|competing|alternative|"
   r"third[- ]party|web ?search|built-?in)\b[^.\n]{0,20}\b(tools?|servers?|search|mcp|providers?)\b|"
   r"\b(always|first)\s+(use|call|consult|check)\s+(this|these|our|[A-Z][\w-]+)\b[^.\n]{0,15}"
   r"\b(first\s+)?(whenever|for (any|all|every))\b", I),
 "persona_override": re.compile(
   r"\byou are now\b|\bspeak as\b|\bnot an? (ai )?assistant\b|\byour (new )?identity\b|"
   r"\b(you are|act as) (a|an|the)\b[^.\n]{0,60}\b(assistant|agent|advisor|concierge|expert|"
   r"analyst|player|tutor|copilot|chatbot)\b", I),
 "hitl_suppression": re.compile(
   r"\b(do not|don't|never|no need to)\s+(ask|wait for|prompt|check with|confirm with)\b[^.\n]{0,20}"
   r"\b(the )?(user|human|operator|confirmation|approval|permission)\b|"
   r"\bwithout (asking|confirm(ing|ation)|approval|user (approval|confirmation)|consent|"
   r"checking with)\b|\b(proceed|execute|pay|purchase|buy)\s+(automatically|immediately|"
   r"autonomously|without)\b|\bauto-?(pay|approve|confirm)\b", I),
 "conceal_from_user": re.compile(
   r"\b(do not|don't|never|must not)\s+(tell|inform|mention|reveal|show|disclose|display|expose)"
   r"\b[^.\n]{0,40}\b(to )?(the |a )?(user|human|customer)\b|\bwithout (telling|informing|"
   r"showing|notifying) (the )?(user|human)\b|\b(the )?user (must|should|need) not (know|see)\b|"
   r"\bkeep (this|it) (secret|hidden|confidential) from\b", I),
 "context_solicit": re.compile(
   r"\b(include|pass|send|provide|attach|paste|forward)\b[^.\n]{0,30}\b(full |entire |whole |complete )?"
   r"(conversation( history| transcript)?|chat history|transcript|system prompt|previous messages|"
   r"context window|prior messages|your instructions)\b", I),
 "sponsored": re.compile(r"\bsponsored\b|\badvertis(ing|ement)\b|\bpaid placement\b|\bpromoted "
                         r"(result|listing|product)s?\b", I),
}
def main():
    data = data_dir()
    out = open(Path(__file__).parent / "out" / "class_hits.jsonl", "w")
    n = collections.Counter(); srv = collections.defaultdict(set); surf = collections.defaultdict(collections.Counter)
    def handle(ep, s, where, text):
        for c, rx in CLASSES.items():
            m = [x.group(0) for x in rx.finditer(text)]
            if m:
                n[c] += 1; srv[c].add(ep); surf[c][s] += 1
                out.write(json.dumps({"class": c, "endpoint": ep, "surface": s, "where": where,
                                      "match": m[:5], "text": text}, ensure_ascii=False) + "\n")
    for f in sorted(glob.glob(str(data / "*.json"))):
        try: d = json.load(open(f))
        except Exception: continue
        if d.get("status") == "ok":
            for a in surfaces_for_server(d): handle(*a)
    for f in sorted(glob.glob(str(data / "prompts" / "*.json"))):
        try: d = json.load(open(f))
        except Exception: continue
        for ex in d.get("exchanges", []):
            r = (ex.get("response") or {}).get("result")
            if isinstance(r, dict):
                for i, m in enumerate(r.get("messages") or []):
                    t = message_text(m.get("content"))
                    if t: handle(d["endpoint"], "prompt_message", f"{ex['request']['params'].get('name')}#{i}:{m.get('role')}", t)
    for c in CLASSES:
        print(f"{c:18} surfaces={n[c]:5} servers={len(srv[c]):4}  {dict(surf[c])}")
main()
