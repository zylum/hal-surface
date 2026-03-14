#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <mode>" >&2
  exit 2
fi

MODE="$1"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="$REPO_DIR/config.json"
TMP_CONFIG="$(mktemp)"

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Missing $CONFIG_PATH" >&2
  exit 1
fi

python3 - "$CONFIG_PATH" "$TMP_CONFIG" "$MODE" <<'PY'
import json
import sys
src, dst, mode = sys.argv[1:4]
with open(src, 'r', encoding='utf-8') as f:
    cfg = json.load(f)
cfg['mode'] = mode
cfg['run_continuous'] = False
with open(dst, 'w', encoding='utf-8') as f:
    json.dump(cfg, f)
PY

if [[ -d "$REPO_DIR/.venv" ]]; then
  "$REPO_DIR/.venv/bin/python" "$REPO_DIR/main.py" --config "$TMP_CONFIG"
else
  python3 "$REPO_DIR/main.py" --config "$TMP_CONFIG"
fi

rm -f "$TMP_CONFIG"
