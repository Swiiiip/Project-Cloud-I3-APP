import logging
import os
from typing import Tuple, Dict

import requests
from dotenv import load_dotenv

from src.config import Config
from src.core.emoji.dto.emoji_data import EmojiData
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler

logger = logging.getLogger(__name__)

class GameClient:
    def __init__(self,
                 base_url: str):
        self._base_url = base_url

    def create_daily_challenge(self, user_id: str) -> Dict:
        url = f"{self._base_url}/api/v1/daily/start/{user_id}"
        logger.info(f"Creating daily challenge for user '{user_id}'")
        response = requests.get(url, json={"user_id": user_id}, timeout=Config.REQUEST_TIMEOUT_SECONDS)
        return response.json()

    def make_guess(self, user_id: str, first_codepoint_guess: str, second_codepoint_guess: str) -> Dict:
        url = f"{self._base_url}/api/v1/daily/guess/{user_id}"
        payload = {"user_id": user_id,
                   "first_codepoint_guess": first_codepoint_guess,
                   "second_codepoint_guess": second_codepoint_guess}
        logger.info(f"Making guess for user '{user_id}' with payload: {payload}")
        response = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT_SECONDS)
        return response.json()

    def get_status(self, user_id: str) -> Dict:
        url = f"{self._base_url}/api/v1/daily/get_status/{user_id}"
        logger.info(f"Fetching status for user '{user_id}'")
        response = requests.get(url, timeout=Config.REQUEST_TIMEOUT_SECONDS)
        return response.json()

    def get_rendered_image_url(self, user_id: str) -> str:
        status_response_json = self.get_status(user_id)
        logger.info(f"Fetching rendered image URL for user '{user_id}' with status response: {status_response_json}")
        return f"{self._base_url}{status_response_json['image_url']}"

    def get_supported_emojis(self) -> Tuple[EmojiData, ...]:
        url = f"{self._base_url}/api/v1/daily/supported_emojis"
        logger.info(f"Fetching supported emojis")
        response = requests.get(url, timeout=Config.REQUEST_TIMEOUT_SECONDS)
        return tuple(EmojiData.from_dict(raw_emoji) for raw_emoji in response.json().get("emojis", []))


if __name__ == '__main__':
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)

    client = GameClient(os.environ["API_BASE_URL"])
    client.create_daily_challenge("daily_user_1")
    x = client.get_rendered_image_url("daily_user_1")
    print(x)
    print(client.make_guess("daily_user_1", first_codepoint_guess="1f600", second_codepoint_guess="1f601"))
