#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICES=("hal-surface.service" "hal-admin.service")

cd "$REPO_DIR"

echo "Fetching latest changes..."
git fetch --all --prune
git pull --ff-only

if [[ -d ".venv" ]]; then
  echo "Updating Python deps in .venv..."
  source .venv/bin/activate
  pip install -r requirements.txt
fi

echo "Restarting services..."
for service in "${SERVICES[@]}"; do
  sudo systemctl restart "$service"
  sudo systemctl status "$service" --no-pager
  echo
done
