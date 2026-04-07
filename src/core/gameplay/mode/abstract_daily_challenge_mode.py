from abc import ABC, abstractmethod

from src.core.gameplay.mode.daily_challenge_results.daily_challenge_guess_result import DailyChallengeGuessResult
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_start_result import DailyChallengeStartResult
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_status_result import DailyChallengeStatusResult
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_end_result import DailyChallengeEndResult
from src.core.gameplay.state.daily_challenge_state import DailyChallengeState


class AbstractDailyChallengeMode(ABC):
    def __init__(self, game_state: DailyChallengeState):
        self.game_state = game_state

    @abstractmethod
    def start_game(self) -> DailyChallengeStartResult:
        pass

    @abstractmethod
    def make_guess(self, guess: str) -> DailyChallengeGuessResult:
        pass

    @abstractmethod
    def get_game_status(self) -> DailyChallengeStatusResult:
        pass

    @abstractmethod
    def end_game(self) -> DailyChallengeEndResult:
        pass
