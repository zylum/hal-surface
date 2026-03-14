"""TTS-only mode."""

from runtime.config import AppConfig
from runtime.state import RuntimeState, StateManager
from runtime.tts import speak


def run(config: AppConfig, state: StateManager) -> None:
    state.set_state(RuntimeState.SPEAKING)
    speak(config.tts_test_phrase, config.tts_engine)
    state.set_state(RuntimeState.IDLE)
