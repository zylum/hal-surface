"""Runtime state handling for hardware-independent surface state."""

from enum import Enum
from typing import Callable, List


class RuntimeState(str, Enum):
    BOOTING = "booting"
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ERROR = "error"


class StateManager:
    def __init__(self) -> None:
        self._state: RuntimeState = RuntimeState.BOOTING
        self._listeners: List[Callable[[RuntimeState], None]] = []

    @property
    def state(self) -> RuntimeState:
        return self._state

    def add_listener(self, callback: Callable[[RuntimeState], None]) -> None:
        self._listeners.append(callback)

    def set_state(self, next_state: RuntimeState) -> None:
        self._state = next_state
        for listener in self._listeners:
            listener(next_state)
