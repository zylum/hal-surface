"""HAL local admin panel (LAN-only)."""

from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from urllib.parse import parse_qs, urlparse

from services.config_store import ConfigStore
from services.logs import recent_logs
from services.supervisor import Supervisor
from runtime.audio import list_audio_devices


VALID_MODES = ["audio_loopback", "tts_only", "voice_stub", "voice_to_aviary"]
PIN = os.environ.get("HAL_ADMIN_PIN", "")


def _bool(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def render_html(config: Dict[str, Any], status: str, logs: str, devices: str, message: str = "") -> str:
    template_path = Path(__file__).parent / "templates" / "index.html"
    html = template_path.read_text(encoding="utf-8")

    options = "\n".join(
        f'<option value="{mode}" {"selected" if config.get("mode") == mode else ""}>{mode}</option>'
        for mode in VALID_MODES
    )

    return (
        html.replace("{{message}}", message)
        .replace("{{mode_options}}", options)
        .replace("{{aviary_url}}", str(config.get("aviary_url", "")))
        .replace("{{record_seconds}}", str(config.get("record_seconds", 5)))
        .replace("{{audio_input_device}}", str(config.get("audio_input_device", 0)))
        .replace("{{audio_output_device}}", str(config.get("audio_output_device", 0)))
        .replace("{{led_checked}}", "checked" if config.get("led_enabled", False) else "")
        .replace("{{tft_checked}}", "checked" if config.get("tft_enabled", False) else "")
        .replace("{{service_status}}", status)
        .replace("{{logs}}", logs)
        .replace("{{devices}}", devices)
        .replace("{{mode}}", str(config.get("mode", "unknown")))
    )


class Handler(BaseHTTPRequestHandler):
    config_store = ConfigStore()
    supervisor = Supervisor()

    def _read_post_data(self) -> Dict[str, str]:
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length).decode("utf-8")
        parsed = parse_qs(payload, keep_blank_values=True)
        return {k: v[0] for k, v in parsed.items()}

    def _authorized(self, form_data: Dict[str, str]) -> bool:
        if not PIN:
            return True
        return form_data.get("pin", "") == PIN

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        config = self.config_store.read()

        if path == "/status":
            self._send_json({"mode": config.get("mode"), "service_status": self.supervisor.service_status()})
            return
        if path == "/config":
            self._send_json(config)
            return
        if path == "/logs":
            self._send_json({"logs": recent_logs(100)})
            return
        if path == "/devices":
            self._send_json({"devices": list_audio_devices()})
            return

        status = self.supervisor.service_status()
        logs = recent_logs(100)
        devices = list_audio_devices()
        self._send_html(render_html(config, status, logs, devices))

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        form = self._read_post_data()
        if not self._authorized(form):
            self._send_json({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
            return

        if path == "/config":
            patch: Dict[str, Any] = {}
            for key in ["mode", "aviary_url", "record_seconds", "audio_input_device", "audio_output_device"]:
                if key in form and form[key] != "":
                    value: Any = form[key]
                    if key in {"record_seconds", "audio_input_device", "audio_output_device"}:
                        value = int(value)
                    patch[key] = value
            patch["led_enabled"] = "led_enabled" in form
            patch["tft_enabled"] = "tft_enabled" in form
            updated = self.config_store.update(patch)
            self._send_json({"ok": True, "config": updated})
            return

        if path == "/mode":
            mode = form.get("mode", "")
            if mode not in VALID_MODES:
                self._send_json({"error": "invalid mode"}, status=400)
                return
            updated = self.config_store.update({"mode": mode})
            self._send_json({"ok": True, "config": updated})
            return

        if path == "/restart":
            self._send_json(self.supervisor.restart_service())
            return

        if path == "/git-pull":
            self._send_json(self.supervisor.git_pull_and_restart())
            return

        if path == "/test/audio":
            self._send_json(self.supervisor.run_loopback_test())
            return

        if path == "/test/tts":
            self._send_json(self.supervisor.run_tts_test())
            return

        self._send_json({"error": "not found"}, status=404)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HAL admin panel")
    parser.add_argument("--host", default="0.0.0.0", help="Host bind (LAN only recommended)")
    parser.add_argument("--port", type=int, default=8787, help="Port to bind")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"HAL admin running on http://{args.host}:{args.port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
