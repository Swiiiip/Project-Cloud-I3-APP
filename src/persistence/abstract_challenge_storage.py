from abc import ABC, abstractmethod
from typing import Optional
from src.core.gameplay.dto.challenge_state import ChallengeState


class AbstractChallengeStorage(ABC):
    @abstractmethod
    def save_state(self, session_id: str, state: ChallengeState) -> None:
        pass

    @abstractmethod
    def get_state(self, session_id: str) -> Optional[ChallengeState]:
        pass

    @abstractmethod
    def delete_state(self, session_id: str) -> None:
        pass
