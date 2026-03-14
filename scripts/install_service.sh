#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICES=("hal-surface.service" "hal-admin.service")

for service in "${SERVICES[@]}"; do
  if [[ ! -f "$REPO_DIR/systemd/$service" ]]; then
    echo "Missing service file: $REPO_DIR/systemd/$service" >&2
    exit 1
  fi
  sudo cp "$REPO_DIR/systemd/$service" "/etc/systemd/system/$service"
done

sudo systemctl daemon-reload

for service in "${SERVICES[@]}"; do
  sudo systemctl enable "$service"
  sudo systemctl restart "$service"
  echo "Installed and started $service"
done

echo "Use: journalctl -u hal-surface.service -f"
echo "Use: journalctl -u hal-admin.service -f"
