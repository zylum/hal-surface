"""Configuration loading and validation."""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List

VALID_MODES = {"audio_loopback", "tts_only", "voice_stub", "voice_to_aviary"}


@dataclass
class AppConfig:
    mode: str
    aviary_url: str
    workspace_id: str
    person_id: str
    device_id: str
    tts_engine: str = "espeak"
    tts_test_phrase: str = "HAL surface test phrase."
    audio_input_device: int = 0
    audio_output_device: int = 0
    record_seconds: int = 5
    transcription_provider: str = "stub"
    stub_transcript: str = "This is a stub transcript."
    stub_responses: List[str] = field(default_factory=lambda: ["Stub response"])
    request_timeout_seconds: int = 15
    run_continuous: bool = False
    loop_delay_seconds: int = 1
    led_enabled: bool = False
    tft_enabled: bool = False
    log_level: str = "info"


def load_config(path: str) -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    _validate_required(raw, ["mode", "aviary_url", "workspace_id", "person_id", "device_id"])
    cfg = AppConfig(**raw)
    _validate_config(cfg)
    return cfg


def _validate_required(raw: Dict[str, Any], required: List[str]) -> None:
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")


def _validate_config(config: AppConfig) -> None:
    if config.mode not in VALID_MODES:
        raise ValueError(f"Invalid mode: {config.mode}. Expected one of: {', '.join(sorted(VALID_MODES))}")
    if config.record_seconds < 1 or config.record_seconds > 30:
        raise ValueError("record_seconds must be between 1 and 30")
    if config.loop_delay_seconds < 0:
        raise ValueError("loop_delay_seconds must be >= 0")
    if config.request_timeout_seconds < 1:
        raise ValueError("request_timeout_seconds must be >= 1")
