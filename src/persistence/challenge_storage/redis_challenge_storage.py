import logging
from typing import Optional

import redis

from src.core.gameplay.dto.challenge_state import ChallengeState
from src.persistence.challenge_storage.abstract_challenge_storage import AbstractChallengeStorage

logger = logging.getLogger(__name__)


class RedisChallengeStorage(AbstractChallengeStorage):
    def __init__(self, host: str, port: int, ttl: int):
        self._client = redis.Redis(host=host, port=port, decode_responses=True)
        self._ttl = ttl
        self._client.ping()

    def save_state(self, session_id: str, state: ChallengeState) -> None:
        state_json = state.model_dump_json()
        self._client.set(session_id, state_json, ex=self._ttl)
        logger.info("Saved challenge state for session %s", session_id)

    def get_state(self, session_id: str) -> Optional[ChallengeState]:
        state_json = self._client.get(session_id)
        if not state_json:
            return None
        return ChallengeState.model_validate_json(state_json)

    def delete_state(self, session_id: str) -> None:
        self._client.delete(session_id)
