import json
import logging
import os
import requests

from src.config import Config


logger = logging.getLogger(__name__)


class EmojiKitchenService:
    def __init__(self):
        self.cache_file = os.path.join(".game_state", "emoji_metadata_cache.json")
        os.makedirs(".game_state", exist_ok=True)

        if self._is_cache_valid():
            logger.info("Loading emoji kitchen metadata from cache...")
            self._load_from_cache()
        else:
            logger.info("Fetching emoji kitchen metadata from remote...")
            self._fetch_and_cache_metadata()

    def _is_cache_valid(self) -> bool:
        if not os.path.exists(self.cache_file):
            return False
        return True

    def _load_from_cache(self) -> None:
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                self.db = cached_data.get("data", {})
                self.supported_emojis = cached_data.get("knownSupportedEmoji", [])
            logger.info(f"Metadata loaded from cache. {len(self.supported_emojis)} emojis supported.")
        except Exception as e:
            logger.error(f"Failed to load emoji kitchen metadata from cache: {e}")
            self._fetch_and_cache_metadata()

    def _fetch_and_cache_metadata(self) -> None:
        try:
            response = requests.get(Config.EMOJI_KITCHEN_METADATA_URL, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            full_json = response.json()

            self.db = full_json.get("data", {})
            self.supported_emojis = full_json.get("knownSupportedEmoji", [])

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(full_json, f, ensure_ascii=False, indent=2)

            logger.info(f"Metadata fetched and cached. {len(self.supported_emojis)} emojis supported.")
        except Exception as e:
            logger.error(f"Failed to fetch emoji kitchen metadata: {e}")
            self.db = {}
            self.supported_emojis = []

    def _get_codepoint(self, emoji: str) -> str:
        return "-".join(f"{ord(c):x}" for c in emoji).lower()

    def is_supported(self, emoji_code: str) -> bool:
        return emoji_code in self.supported_emojis

    def get_mixed_emoji_url(self, emoji1: str, emoji2: str):
        c1 = self._get_codepoint(emoji1)
        c2 = self._get_codepoint(emoji2)

        if not self.is_supported(c1):
            return {"error": f"Emoji {emoji1} (u{c1}) is not supported by Emoji Kitchen."}
        if not self.is_supported(c2):
            return {"error": f"Emoji {emoji2} (u{c2}) is not supported by Emoji Kitchen."}

        result = self._search_metadata(c1, c2) or self._search_metadata(c2, c1)

        if result:
            return result

        return {"error": "No combination exists for these two specific emojis."}

    def _search_metadata(self, base_code, combo_code):
        if base_code in self.db:
            combinations = self.db[base_code].get("combinations", {})
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

    def get_mixed_emoji_bytes(self, emoji1: str, emoji2: str):
        result = self.get_mixed_emoji_url(emoji1, emoji2)
        if "error" in result:
            return None

        response = requests.get(result["image_url"])
        return response.content if response.status_code == 200 else None


if __name__ == "__main__":
    kitchen = EmojiKitchenService()

    logger.info("Test 1 (Ghost + Coffee): %s", kitchen.get_mixed_emoji_url("👻", "☕"))

    logger.info("Test 2 (Invalid): %s", kitchen.get_mixed_emoji_url("💙", "🧬"))
