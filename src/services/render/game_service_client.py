import requests

from src.core.gameplay.dto.challenge_state import ChallengeState


class GameServiceClient:
    def __init__(self, game_service_base_url: str, timeout_seconds: int):
        self._base_url = game_service_base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._session = requests.Session()

    def get_status(self, session_id: str) -> ChallengeState:
        response = self._session.get(
            f"{self._base_url}/internal/game/status",
            params={"session_id": session_id},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        return ChallengeState.model_validate(response.json())

