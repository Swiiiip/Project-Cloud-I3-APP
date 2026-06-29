import requests

from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple


class InternalServiceClient:
    def __init__(
        self,
        game_engine_service_base_url: str,
        emoji_catalog_service_base_url: str,
        emoji_render_service_base_url: str,
        timeout_seconds: int,
    ):
        self._game_engine_service_base_url = game_engine_service_base_url.rstrip("/")
        self._emoji_catalog_service_base_url = emoji_catalog_service_base_url.rstrip("/")
        self._emoji_render_service_base_url = emoji_render_service_base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def start_game(self, session_id: str) -> dict:
        with requests.Session() as session:
            response = session.get(
                f"{self._game_engine_service_base_url}/internal/game_engine/start",
                params={"session_id": session_id},
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            return response.json()

    def submit_guess(self, session_id: str, guess: EmojiCodepointCouple) -> dict:
        with requests.Session() as session:
            response = session.post(
                f"{self._game_engine_service_base_url}/internal/game_engine/guess",
                json={"session_id": session_id, "guess": guess.model_dump()},
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            return response.json()

    def get_status(self, session_id: str) -> dict:
        with requests.Session() as session:
            response = session.get(
                f"{self._game_engine_service_base_url}/internal/game_engine/status",
                params={"session_id": session_id},
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            return response.json()

    def get_supported_emojis(self) -> dict:
        with requests.Session() as session:
            response = session.get(
                f"{self._emoji_catalog_service_base_url}/internal/emoji_catalog/supported_emojis",
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            return response.json()

    def get_rendered_image(self, session_id: str) -> bytes:
        with requests.Session() as session:
            response = session.get(
                f"{self._emoji_render_service_base_url}/internal/emoji_render/image",
                params={"session_id": session_id},
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            return response.content

