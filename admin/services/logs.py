"""Journal log reader helpers."""

from __future__ import annotations

import subprocess

SERVICE_NAME = "hal-surface.service"


def recent_logs(lines: int = 100) -> str:
    cmd = ["journalctl", "-u", SERVICE_NAME, "-n", str(lines), "--no-pager"]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    return (result.stdout or result.stderr).strip()
