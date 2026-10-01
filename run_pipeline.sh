#!/usr/bin/env bash
# Full discovery pipeline: directories -> merged endpoint pool -> MCP discovery.
# Discovery only (initialize, tools/list, resources/list, prompts/list, prompts/get);
# it never calls a tool. Every step is resumable: just run the script again.
#
#   ./run_pipeline.sh            # everything
#   ./run_pipeline.sh --skip-collect   # reuse the directory listings already in directories/raw/
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p directories/logs

if [[ "${1:-}" != "--skip-collect" ]]; then
  echo "[1/3] collecting listings from the public MCP directories (several hours for glama/mcpso)"
  for s in official smithery glama mcpso mcpdirectory; do
    python3 directories/collect.py --source "$s" > "directories/logs/$s.log" 2>&1 &
  done
  wait
fi

echo "[2/3] merging and de-duplicating endpoints -> directories/endpoints.csv"
python3 directories/merge.py

echo "[3/3] MCP discovery on the whole pool -> data/<today>/"
python3 discover.py --concurrency 10
