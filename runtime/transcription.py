"""Transcription provider abstraction."""

from runtime.config import AppConfig


def transcribe_audio(config: AppConfig, _audio_path: str) -> str:
    """Return transcript text for an audio file.

    v1 intentionally supports only a stub transcript so runtime behavior
    is deterministic during early bring-up.
    """
    if config.transcription_provider == "stub":
        return config.stub_transcript
    raise ValueError(f"Unsupported transcription_provider: {config.transcription_provider}")
