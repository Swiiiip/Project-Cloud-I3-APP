import io
import logging
from typing import Tuple

import requests
from PIL.Image import Image, open

from src.config import Config
from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple
from src.core.emoji.dto.emoji_data import EmojiData
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

    def get_supported_emojis(self) -> Tuple[EmojiData, ...]:
        url = f"{self._base_url}/api/v1/daily/supported_emojis"
        response = self._session.get(url, timeout=Config.REQUEST_TIMEOUT_SECONDS)
        data = response.json().get("emojis", [])
        return tuple(EmojiData.from_dict(raw_emoji) for raw_emoji in data)

    def get_rendered_image(self) -> Image:
        url = f"{self._base_url}/api/v1/daily/render"
        response = self._session.get(url, timeout=Config.REQUEST_TIMEOUT_SECONDS)
        return open(io.BytesIO(response.content))


if __name__ == '__main__':
    from src.utils.logger_coonfigurator import LoggerConfigurator
    from src.utils.path_handler import PathHandler
    from dotenv import load_dotenv
    import os

    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)

    client = GameClient(os.environ["API_BASE_URL"])
    client.create_daily_challenge()
    rendered_image_object = client.get_rendered_image()
    rendered_image_object.save("INITIAL-rendered_image.png")
    print(client.get_status())
    print(f"Session Cookie: {client._session.cookies.get_dict()}")

    couple_guess = EmojiCodepointCouple("1f3d1", "1f365")
    print(client.make_guess(couple_guess))
    print(client.get_status())
    print(f"Session Cookie: {client._session.cookies.get_dict()}")

    rendered_image_object = client.get_rendered_image()
    rendered_image_object.save("GUESS1-rendered_image.png")
