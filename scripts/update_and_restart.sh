#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="hal-surface.service"

cd "$REPO_DIR"

echo "Fetching latest changes..."
git fetch --all --prune
git pull --ff-only

if [[ -d ".venv" ]]; then
  echo "Updating Python deps in .venv..."
  source .venv/bin/activate
  pip install -r requirements.txt
fi

echo "Restarting service..."
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager
