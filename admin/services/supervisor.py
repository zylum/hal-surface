"""Thin wrappers around controlled service operations."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Dict

SERVICE_NAME = "hal-surface.service"
DEFAULT_REPO_DIR = Path(os.environ.get("HAL_SURFACE_REPO", "~/apps/hal-surface")).expanduser()


class Supervisor:
    def __init__(self, repo_dir: Path | None = None) -> None:
        self.repo_dir = repo_dir or DEFAULT_REPO_DIR

    def service_status(self) -> str:
        cmd = ["systemctl", "status", SERVICE_NAME, "--no-pager", "--lines=10"]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        return (result.stdout or result.stderr).strip()

    def restart_service(self) -> Dict[str, str | int]:
        script = self.repo_dir / "scripts" / "restart_service.sh"
        result = subprocess.run([str(script)], check=False, capture_output=True, text=True)
        return {"returncode": result.returncode, "output": (result.stdout + result.stderr).strip()}

    def git_pull_and_restart(self) -> Dict[str, str | int]:
        script = self.repo_dir / "scripts" / "update_and_restart.sh"
        result = subprocess.run([str(script)], check=False, capture_output=True, text=True)
        return {"returncode": result.returncode, "output": (result.stdout + result.stderr).strip()}

    def run_loopback_test(self) -> Dict[str, str | int]:
        script = self.repo_dir / "scripts" / "run_mode_once.sh"
        result = subprocess.run([str(script), "audio_loopback"], check=False, capture_output=True, text=True)
        return {"returncode": result.returncode, "output": (result.stdout + result.stderr).strip()}

    def run_tts_test(self) -> Dict[str, str | int]:
        script = self.repo_dir / "scripts" / "run_mode_once.sh"
        result = subprocess.run([str(script), "tts_only"], check=False, capture_output=True, text=True)
        return {"returncode": result.returncode, "output": (result.stdout + result.stderr).strip()}
