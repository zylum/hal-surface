#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="hal-surface.service"

if [[ ! -f "$REPO_DIR/systemd/$SERVICE_NAME" ]]; then
  echo "Missing service file at $REPO_DIR/systemd/$SERVICE_NAME" >&2
  exit 1
fi

sudo cp "$REPO_DIR/systemd/$SERVICE_NAME" "/etc/systemd/system/$SERVICE_NAME"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "Installed and started $SERVICE_NAME"
echo "Use: journalctl -u $SERVICE_NAME -f"
