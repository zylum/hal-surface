"""Audio loopback mode."""

import logging

from runtime import audio
from runtime.config import AppConfig
from runtime.state import RuntimeState, StateManager


def run(config: AppConfig, state: StateManager) -> None:
    state.set_state(RuntimeState.LISTENING)
    wav = audio.record_wav(config.record_seconds, config.audio_input_device)
    logging.info("Recorded audio to %s", wav)

    state.set_state(RuntimeState.SPEAKING)
    audio.play_wav(wav, config.audio_output_device)

    state.set_state(RuntimeState.IDLE)
