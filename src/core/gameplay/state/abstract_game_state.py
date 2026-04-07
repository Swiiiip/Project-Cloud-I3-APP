from abc import ABC, abstractmethod
from typing import Union

from src.core.gameplay.state.daily_challenge_state_snapshot import DailyChallengeStateSnapshot
from src.core.gameplay.state.endless_mode_state_snapshot import EndlessModeStateSnapshot


class AbstractGameState(ABC):
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.score = 0
        self.attempts = 0
        self.is_completed = False

    @abstractmethod
    def to_snapshot(
        self,
    ) -> Union[DailyChallengeStateSnapshot, EndlessModeStateSnapshot]:
        pass

    @abstractmethod
    def update_score(self, points: int) -> None:
        pass

    @abstractmethod
    def increment_attempts(self) -> None:
        pass

    @abstractmethod
    def complete_game(self) -> None:
        pass
