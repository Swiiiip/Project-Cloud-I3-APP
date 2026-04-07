from abc import ABC, abstractmethod

from src.core.gameplay.mode.endless_mode_results.endless_mode_end_result import EndlessModeEndResult
from src.core.gameplay.mode.endless_mode_results.endless_mode_guess_result import EndlessModeGuessResult
from src.core.gameplay.mode.endless_mode_results.endless_mode_start_result import EndlessModeStartResult
from src.core.gameplay.mode.endless_mode_results.endless_mode_status_result import EndlessModeStatusResult
from src.core.gameplay.state.endless_mode_state import EndlessModeState


class AbstractEndlessMode(ABC):
    def __init__(self, game_state: EndlessModeState):
        self.game_state = game_state

    @abstractmethod
    def start_game(self) -> EndlessModeStartResult:
        pass

    @abstractmethod
    def make_guess(self, guess: str) -> EndlessModeGuessResult:
        pass

    @abstractmethod
    def get_game_status(self) -> EndlessModeStatusResult:
        pass

    @abstractmethod
    def end_game(self) -> EndlessModeEndResult:
        pass
