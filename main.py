"""Entry point for hal-surface runtime."""

import argparse
import logging
import sys
import time
from typing import Callable, Dict

from modes import audio_loopback, tts_only, voice_stub, voice_to_aviary
from runtime import audio
from runtime.config import AppConfig, load_config
from runtime.led import LEDRenderer
from runtime.state import RuntimeState, StateManager
from runtime.tft import TFTRenderer

ModeHandler = Callable[[AppConfig, StateManager], None]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HAL surface runtime")
    parser.add_argument("--config", default="config.json", help="Path to config JSON")
    parser.add_argument("--list-devices", action="store_true", help="Print audio devices and exit")
    return parser.parse_args()


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )


def build_mode_map() -> Dict[str, ModeHandler]:
    return {
        "audio_loopback": audio_loopback.run,
        "tts_only": tts_only.run,
        "voice_stub": voice_stub.run,
        "voice_to_aviary": voice_to_aviary.run,
    }


def run_once(handler: ModeHandler, config: AppConfig, state: StateManager) -> int:
    started = time.monotonic()
    try:
        handler(config, state)
    except Exception:
        logging.exception("Runtime error while executing mode=%s", config.mode)
        state.set_state(RuntimeState.ERROR)
        return 1

    elapsed = time.monotonic() - started
    logging.info("Mode run finished mode=%s elapsed=%.3fs", config.mode, elapsed)
    return 0


def main() -> int:
    args = parse_args()

    if args.list_devices:
        print(audio.list_audio_devices())
        return 0

    config = load_config(args.config)
    setup_logging(config.log_level)

    logging.info("Starting hal-surface")
    logging.info("Mode=%s", config.mode)
    logging.info("Continuous=%s loop_delay_seconds=%s", config.run_continuous, config.loop_delay_seconds)
    logging.info(
        "Audio devices input=%s output=%s",
        config.audio_input_device,
        config.audio_output_device,
    )

    state = StateManager()
    led = LEDRenderer(config.led_enabled)
    tft = TFTRenderer(config.tft_enabled)

    def on_state_change(next_state: RuntimeState) -> None:
        logging.info("State transition -> %s", next_state.value)
        led.render(next_state)
        tft.render(next_state)

    state.add_listener(on_state_change)
    state.set_state(RuntimeState.IDLE)

    mode_map = build_mode_map()
    handler = mode_map.get(config.mode)
    if handler is None:
        logging.error("Unsupported mode: %s", config.mode)
        return 2

    if not config.run_continuous:
        return run_once(handler, config, state)

    while True:
        code = run_once(handler, config, state)
        if code != 0:
            return code
        time.sleep(config.loop_delay_seconds)


if __name__ == "__main__":
    sys.exit(main())
