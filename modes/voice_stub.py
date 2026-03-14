"""Voice stub mode."""

import logging
import random

from runtime import audio
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
    logging.info("Stub transcript: %s", transcript)

    state.set_state(RuntimeState.SPEAKING)
    response = random.choice(config.stub_responses) if config.stub_responses else "Stub response"
    speak(response, config.tts_engine)

    state.set_state(RuntimeState.IDLE)
