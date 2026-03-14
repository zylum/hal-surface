"""Optional LED ring renderer."""

import logging

from runtime.state import RuntimeState


class LEDRenderer:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def render(self, state: RuntimeState) -> None:
        if not self.enabled:
            return
        logging.info("[led] render state=%s", state.value)
