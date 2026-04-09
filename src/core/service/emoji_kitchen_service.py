import json
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv
from typing import Tuple

from src.persistence.file_emoji_repository import FileEmojiRepository
from src.persistence.abstract_emoji_repository import AbstractEmojiRepository
from src.core.dto.emoji_data import EmojiData
from src.config import Config
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler

logger = logging.getLogger(__name__)


class EmojiKitchenService:

    def __init__(self,
                 db: AbstractEmojiRepository):
        # self._db = db
        self._db = {}
        cache_dir = PathHandler.cache_dir()
        self._cache_file = cache_dir / "emoji_metadata_cache.json"
        Path.mkdir(cache_dir, exist_ok=True)

        if self._cache_file.exists():
            logger.info("Loading emoji kitchen metadata from cache...")
            self._load_from_cache()
        else:
            logger.info("Fetching emoji kitchen metadata from remote...")
            self._fetch_and_cache_metadata()

    def get_mixed_emoji_url(self, emoji1: str, emoji2: str):
        c1 = self._get_codepoint(emoji1)
        c2 = self._get_codepoint(emoji2)

        if not self._is_supported(c1):
            return {"error": f"Emoji {emoji1} (u{c1}) is not supported by Emoji Kitchen."}
        if not self._is_supported(c2):
            return {"error": f"Emoji {emoji2} (u{c2}) is not supported by Emoji Kitchen."}

        result = self._search_metadata(c1, c2) or self._search_metadata(c2, c1)

        if result:
            return result

        return {"error": "No combination exists for these two specific emojis."}

    def get_mixed_emoji_image_bytes(self, emoji1: str, emoji2: str):
        result = self.get_mixed_emoji_url(emoji1, emoji2)
        if "error" in result:
            return None

        response = requests.get(result["image_url"])
        return response.content if response.status_code == 200 else None

    def get_supported_emojis(self) -> Tuple[EmojiData, ...]:
        return tuple([EmojiData(name=emoji_code,
                                codepoint=emoji_code)
                      for emoji_code in self.supported_emoji_codes])

    def _load_from_cache(self):
        try:
            with open(self._cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                self._db = cached_data.get("data", {})
                self.supported_emoji_codes = cached_data.get("knownSupportedEmoji", [])
            logger.info(f"Metadata loaded from cache. {len(self.supported_emoji_codes)} emojis supported.")
        except Exception as e:
            logger.error(f"Failed to load emoji kitchen metadata from cache: {e}")
            self._fetch_and_cache_metadata()

    def _fetch_and_cache_metadata(self):
        try:
            response = requests.get(Config.EMOJI_KITCHEN_METADATA_URL, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            full_json = response.json()

            self._db = full_json.get("data", {})
            self.supported_emoji_codes = full_json.get("knownSupportedEmoji", [])

            with open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(full_json, f, ensure_ascii=False, indent=2)

            logger.info(f"Metadata fetched and cached. {len(self.supported_emoji_codes)} emojis supported.")
        except Exception as e:
            logger.error(f"Failed to fetch emoji kitchen metadata: {e}")
            self._db = {}
            self.supported_emoji_codes = []

    @staticmethod
    def _get_codepoint(emoji: str) -> str:
        return "-".join(f"{ord(c):x}" for c in emoji).lower()

    def _is_supported(self, emoji_code: str) -> bool:
        return emoji_code in self.supported_emoji_codes

    def _search_metadata(self, base_code, combo_code):
        if base_code in self._db:
            combinations = self._db[base_code].get("combinations", {})
            if combo_code in combinations:
                combo_list = combinations[combo_code]
                if combo_list:
                    match = combo_list[0]
                    return {
                        "image_url": match.get("gStaticUrl"),
                        "alt": match.get("alt"),
                        "date": match.get("date")
                    }
        return None


if __name__ == "__main__":
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)
    kitchen = EmojiKitchenService(FileEmojiRepository(cache_path=PathHandler.cache_dir()))

    print(f"Test 1 (Ghost + Coffee): {kitchen.get_mixed_emoji_url("👻", "☕")}")
    print(f"Test 2 (Invalid): {kitchen.get_mixed_emoji_url("💙", "😚")}")
