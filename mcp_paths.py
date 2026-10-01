"""Shared path helper: which crawl folder the analysis scripts read.

By default the newest data/<YYYY-MM-DD>/ folder written by discover.py is used.
Set MCP_DATA_DIR to analyse a specific crawl, e.g.
    MCP_DATA_DIR=data/2026-09-30 python3 analysis/ads_scan.py
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def data_dir() -> Path:
    env = os.environ.get("MCP_DATA_DIR")
    if env:
        p = Path(env)
        return p if p.is_absolute() else ROOT / p
    runs = sorted(p for p in (ROOT / "data").glob("20??-??-??") if p.is_dir())
    if not runs:
        raise SystemExit("no crawl found in data/ - run discover.py first (see README)")
    return runs[-1]
