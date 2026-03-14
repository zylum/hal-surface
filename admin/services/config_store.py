"""Config read/write helpers for HAL admin."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


DEFAULT_CONFIG_PATH = Path(os.environ.get("HAL_SURFACE_CONFIG", "~/apps/hal-surface/config.json")).expanduser()


class ConfigStore:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or DEFAULT_CONFIG_PATH

    def read(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {}
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def write(self, data: Dict[str, Any]) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def update(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        existing = self.read()
        existing.update(patch)
        self.write(existing)
        return existing
