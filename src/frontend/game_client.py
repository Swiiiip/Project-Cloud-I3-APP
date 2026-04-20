import io
import logging

import requests
from PIL.Image import Image, open

from src.config import Config
from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple
from src.core.emoji.dto.emoji_category_data import EmojiCategoryData
from src.core.gameplay.dto.challenge_state import ChallengeState

logger = logging.getLogger(__name__)


class GameClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._session = requests.Session()

    def create_daily_challenge(self) -> ChallengeState:
        url = f"{self._base_url}/api/v1/daily/start"
        response = self._session.get(url, timeout=Config.REQUEST_TIMEOUT_SECONDS)
        return ChallengeState.model_validate(response.json())

    def make_guess(self, couple_codepoint_guess: EmojiCodepointCouple) -> ChallengeState:
        url = f"{self._base_url}/api/v1/daily/guess"
        response = self._session.post(
            url,
            json=couple_codepoint_guess.model_dump(),
            timeout=Config.REQUEST_TIMEOUT_SECONDS
        )
        return ChallengeState.model_validate(response.json())

    def get_status(self) -> ChallengeState:
        url = f"{self._base_url}/api/v1/daily/get_status"
        response = self._session.get(url, timeout=Config.REQUEST_TIMEOUT_SECONDS)
        return ChallengeState.model_validate(response.json())

    def get_supported_emojis(self) -> tuple[EmojiCategoryData, ...]:
        url = f"{self._base_url}/api/v1/daily/supported_emojis"
        response = self._session.get(url, timeout=Config.REQUEST_TIMEOUT_SECONDS)
        data = response.json().get("categories", [])
        return tuple(EmojiCategoryData.from_dict(raw_category) for raw_category in data)

    def get_rendered_image(self) -> Image:
        url = f"{self._base_url}/api/v1/daily/render"
        response = self._session.get(url, timeout=Config.REQUEST_TIMEOUT_SECONDS)
        return open(io.BytesIO(response.content))
