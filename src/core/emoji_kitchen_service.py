import logging
import requests
from src.config.config import Config
from src.dtos.emoji_combination_response import EmojiCombinationResponse
from src.dtos.error_response import error_response

logger = logging.getLogger(__name__)


class EmojiKitchenService:
    def __init__(self, config: Config):
        logger.info("Loading emoji kitchen metadata...")
        self.config = config
        response = requests.get(
            self.config.emoji_kitchen_metadata_url,
            timeout=self.config.enable_request_timeout
        )
        full_json = response.json()

        # Extract the specific parts we need
        self.db = full_json.get("data", {})
        self.supported_list = full_json.get("knownSupportedEmoji", [])

        logger.info(f"Metadata loaded. {len(self.supported_list)} emojis supported.")

    def _get_codepoint(self, emoji: str) -> str:
        """
        Converts emoji to the hex string format used in the metadata.
        Note: The metadata list uses lowercase (e.g., '1f600').
        """
        return "-".join(f"{ord(c):x}" for c in emoji).lower()

    def _get_emoji_from_codepoint(self, codepoint: str) -> str:
        """
        Converts hex string format to emoji.
        Handles dash-separated codepoints.
        """
        parts = codepoint.split("-")
        return "".join(chr(int(part, 16)) for part in parts)

    def is_supported(self, emoji_code: str) -> bool:
        """Checks if the codepoint exists in the knownSupportedEmoji list."""
        # Some emojis in the list include the variation selector (fe0f),
        # while others don't. We check the exact string.
        return emoji_code in self.supported_list

    def get_mixed_emoji_url(self, emoji1: str, emoji2: str):
        c1 = self._get_codepoint(emoji1)
        c2 = self._get_codepoint(emoji2)

        if not self.is_supported(c1):
            return error_response(f"Emoji {emoji1} (u{c1}) is not supported by Emoji Kitchen.")
        if not self.is_supported(c2):
            return error_response(f"Emoji {emoji2} (u{c2}) is not supported by Emoji Kitchen.")

        result = self._search_metadata(c1, c2) or self._search_metadata(c2, c1)

        if result:
            return result.to_dict()

        return error_response("No combination exists for these two specific emojis.")

    def _search_metadata(self, base_code, combo_code):
        if base_code in self.db:
            combinations = self.db[base_code].get("combinations", {})
            if combo_code in combinations:
                combo_list = combinations[combo_code]
                if combo_list:
                    match = combo_list[0]
                    return EmojiCombinationResponse(
                        image_url=match.get("gStaticUrl"),
                        alt=match.get("alt"),
                        date=match.get("date")
                    )
        return None

    def get_mixed_emoji_bytes(self, emoji1: str, emoji2: str):
        """Fetches the actual image bytes."""
        result = self.get_mixed_emoji_url(emoji1, emoji2)
        if "error" in result:
            return None
        response = requests.get(result["image_url"])
        return response.content if response.status_code == 200 else None

    def get_random_combination(self):
        """Returns two emojis that form a valid combination."""
        import random
        base_codes = list(self.db.keys())
        if not base_codes:
            return None
        max_attempts = 100  # Prevent infinite loop
        for _ in range(max_attempts):
            base_code = random.choice(base_codes)
            combinations = self.db[base_code].get("combinations", {})
            combo_codes = list(combinations.keys())
            if combo_codes:
                combo_code = random.choice(combo_codes)
                emoji1 = self._get_emoji_from_codepoint(base_code)
                emoji2 = self._get_emoji_from_codepoint(combo_code)
                return [emoji1, emoji2]
        return None


if __name__ == "__main__":
    config = Config.from_environment()
    kitchen = EmojiKitchenService(config)
    print("Test 1 (Ghost + Coffee):", kitchen.get_mixed_emoji_url("👻", "☕"))
    print("Test 2 (Random Combination):", kitchen.get_random_combination())
