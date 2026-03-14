"""Text-to-speech abstractions."""

import subprocess


def speak(text: str, engine: str = "espeak") -> None:
    if engine != "espeak":
        raise ValueError(f"Unsupported tts_engine: {engine}")

    subprocess.run(["espeak", text], check=True)
