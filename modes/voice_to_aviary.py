"""Voice to Aviary mode."""

import logging

from runtime import audio
from runtime.aviary_client import post_message
from runtime.config import AppConfig
from runtime.state import RuntimeState, StateManager
from runtime.transcription import transcribe_audio
from runtime.tts import speak


def run(config: AppConfig, state: StateManager) -> None:
    state.set_state(RuntimeState.LISTENING)
    wav = audio.record_wav(config.record_seconds, config.audio_input_device)
    logging.info("Recorded audio to %s", wav)

    state.set_state(RuntimeState.THINKING)
    transcript = transcribe_audio(config, str(wav))
    logging.info("Transcript: %s", transcript)

    response, raw = post_message(
        url=config.aviary_url,
        workspace_id=config.workspace_id,
        person_id=config.person_id,
        device_id=config.device_id,
        text=transcript,
        timeout_seconds=config.request_timeout_seconds,
    )
    logging.info(
        "Aviary status=%s latency=%.3fs assistant_message=%s",
        response.status_code,
        response.latency_seconds,
        response.assistant_message,
    )
    logging.debug("Aviary raw response: %s", raw)

    state.set_state(RuntimeState.SPEAKING)
    speak_text = response.speak_text or response.assistant_message
    if not speak_text:
        speak_text = "I received an empty response from Aviary."
    speak(speak_text, config.tts_engine)

    state.set_state(RuntimeState.IDLE)
