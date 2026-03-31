from abc import ABC, abstractmethod
from src.dtos.daily_challenge_state import DailyChallengeState


class AbstractGameStateStore(ABC):
    @abstractmethod
    def save_daily_challenge(self, user_id: str, state: DailyChallengeState) -> None:
        pass

    @abstractmethod
    def load_daily_challenge(self, user_id: str, challenge_date: str) -> DailyChallengeState | None:
        pass

    @abstractmethod
    def exists_daily_challenge(self, user_id: str, challenge_date: str) -> bool:
        pass
