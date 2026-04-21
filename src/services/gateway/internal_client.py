import requests

from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple


class InternalServiceClient:
    def __init__(
        self,
        game_service_base_url: str,
        catalog_service_base_url: str,
        render_service_base_url: str,
        timeout_seconds: int,
    ):
        self._game_service_base_url = game_service_base_url.rstrip("/")
        self._catalog_service_base_url = catalog_service_base_url.rstrip("/")
        self._render_service_base_url = render_service_base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._session = requests.Session()

    def start_game(self, session_id: str) -> dict:
        response = self._session.get(
            f"{self._game_service_base_url}/internal/game/start",
            params={"session_id": session_id},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def submit_guess(self, session_id: str, guess: EmojiCodepointCouple) -> dict:
        response = self._session.post(
            f"{self._game_service_base_url}/internal/game/guess",
            json={"session_id": session_id, "guess": guess.model_dump()},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def get_status(self, session_id: str) -> dict:
        response = self._session.get(
            f"{self._game_service_base_url}/internal/game/status",
            params={"session_id": session_id},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def get_supported_emojis(self) -> dict:
        response = self._session.get(
            f"{self._catalog_service_base_url}/internal/catalog/supported_emojis",
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def get_rendered_image(self, session_id: str) -> bytes:
        response = self._session.get(
            f"{self._render_service_base_url}/internal/render/image",
            params={"session_id": session_id},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        return response.content

