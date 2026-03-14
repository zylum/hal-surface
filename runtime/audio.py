"""Audio helpers using shell-level ALSA tools for reliability on Pi."""

from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Optional


def ensure_binary(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required binary not found: {name}")


def list_audio_devices() -> str:
    if shutil.which("arecord") is None and shutil.which("aplay") is None:
        return "arecord/aplay are not installed. Install alsa-utils to list devices."

    capture_text = "arecord is not installed."
    playback_text = "aplay is not installed."

    if shutil.which("arecord") is not None:
        capture = subprocess.run(["arecord", "-l"], check=False, capture_output=True, text=True)
        capture_text = capture.stdout or capture.stderr

    if shutil.which("aplay") is not None:
        playback = subprocess.run(["aplay", "-l"], check=False, capture_output=True, text=True)
        playback_text = playback.stdout or playback.stderr

    return (
        "=== Capture devices (arecord -l) ===\n"
        f"{capture_text}\n"
        "=== Playback devices (aplay -l) ===\n"
        f"{playback_text}"
    )


def record_wav(seconds: int, input_device: int, output_path: Optional[Path] = None) -> Path:
    ensure_binary("arecord")
    if output_path is None:
        output_path = Path(tempfile.gettempdir()) / "hal_surface_input.wav"

    cmd = [
        "arecord",
        "-D",
        f"hw:{input_device},0",
        "-f",
        "S16_LE",
        "-r",
        "16000",
        "-c",
        "1",
        "-d",
        str(seconds),
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
    return output_path


def play_wav(path: Path, output_device: int) -> None:
    ensure_binary("aplay")
    cmd = ["aplay", "-D", f"hw:{output_device},0", str(path)]
    subprocess.run(cmd, check=True)
