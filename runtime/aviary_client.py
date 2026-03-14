"""Aviary HTTP client."""

from dataclasses import dataclass
import json
import time
from typing import Any, Dict, Optional, Tuple
from urllib import error, request


@dataclass
class AviaryResponse:
    assistant_message: str
    speak_text: Optional[str]
    status_code: int
    latency_seconds: float


def post_message(
    url: str,
    workspace_id: str,
    person_id: str,
    device_id: str,
    text: str,
    timeout_seconds: int,
) -> Tuple[AviaryResponse, Dict[str, Any]]:
    payload = {
        "workspace_id": workspace_id,
        "person_id": person_id,
        "device_id": device_id,
        "message": text,
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.monotonic()
    try:
        with request.urlopen(req, timeout=timeout_seconds) as resp:
            status_code = resp.status
            raw_body = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        raise RuntimeError(f"Aviary HTTP error {exc.code}: {exc.reason}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Aviary connection error: {exc.reason}") from exc

    latency = time.monotonic() - started
    data = json.loads(raw_body)
    assistant_message = data.get("assistant_message", "")
    speak_text = (data.get("audio") or {}).get("speak_text")

    parsed = AviaryResponse(
        assistant_message=assistant_message,
        speak_text=speak_text,
        status_code=status_code,
        latency_seconds=latency,
    )
    return parsed, data
