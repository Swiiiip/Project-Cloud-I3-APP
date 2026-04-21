import threading
from typing import Optional

from src.core.gameplay.dto.challenge_state import ChallengeState
from src.persistence.challenge_storage.abstract_challenge_storage import AbstractChallengeStorage


class InMemoryChallengeStorage(AbstractChallengeStorage):
    def __init__(self):
        self._states: dict[str, str] = {}
        self._lock = threading.Lock()

    def save_state(self, session_id: str, state: ChallengeState) -> None:
        with self._lock:
            self._states[session_id] = state.model_dump_json()

    def get_state(self, session_id: str) -> Optional[ChallengeState]:
        with self._lock:
            state_json = self._states.get(session_id)
        if state_json is None:
            return None
        return ChallengeState.model_validate_json(state_json)

    def delete_state(self, session_id: str) -> None:
        with self._lock:
            self._states.pop(session_id, None)

