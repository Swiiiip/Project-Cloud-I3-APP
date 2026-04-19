import logging
from typing import Tuple

from src.core.emoji.dto.combination_data import CombinationData
from src.core.emoji.dto.emoji_couple import EmojiDataCouple
from src.core.emoji.dto.emoji_data import EmojiData
from src.core.emoji.emoji_data_populator import EmojiDataPopulator
from src.persistence.abstract_emoji_repository import AbstractEmojiRepository

logger = logging.getLogger(__name__)


class EmojiKitchenService:
    def __init__(self, repository: AbstractEmojiRepository):
        self._repository = repository
        self._populate_repository()

    def fetch_combination_data(self,
                               first_emoji_codepoint: str,
                               second_emoji_codepoint: str) -> CombinationData:
        logger.info("Fetching combination for codepoints: %s and %s", first_emoji_codepoint, second_emoji_codepoint)
        first_emoji = self.fetch_emoji_by_codepoint(first_emoji_codepoint)
        second_emoji = self.fetch_emoji_by_codepoint(second_emoji_codepoint)

        first_raw_combinations = self._get_available_raw_combinations_for_codepoint(first_emoji_codepoint)
        first_raw_combination = first_raw_combinations.get(second_emoji_codepoint, {})
        if first_raw_combination == {}:
            second_raw_combinations = self._get_available_raw_combinations_for_codepoint(second_emoji_codepoint)
            raw_combination = second_raw_combinations.get(first_emoji_codepoint, {})
        else:
            raw_combination = first_raw_combination
        if not raw_combination:
            raise ValueError("No combination found in emoji repository for codepoints: %s and %s",
                             first_emoji_codepoint, second_emoji_codepoint)

        return CombinationData(
            emoji_couple=EmojiDataCouple(first_emoji, second_emoji),
            result_image_url=raw_combination["resultImageUrl"],
            name=raw_combination["name"]
        )

    def fetch_available_codepoints_for_combination(self, reference_codepoint: str) -> Tuple[str]:
        raw_combinations = self._get_available_raw_combinations_for_codepoint(reference_codepoint)
        return tuple(raw_combinations.keys())

    def fetch_emoji_by_codepoint(self, codepoint: str) -> EmojiData:
        with self._repository as repo:
            raw_emoji = repo.get_raw_emoji(codepoint)
            if not raw_emoji:
                raise ValueError(f"Could not fetch emoji with codepoint '{codepoint}'")
            return EmojiData.from_dict(raw_emoji)

    def fetch_all_supported_emoji_codepoints(self) -> Tuple[str, ...]:
        with self._repository as repo:
            raw_data = repo.get_all_raw_emojis()
            return tuple(raw["codepoint"] for raw in raw_data.values())

    def fetch_all_supported_emoji_metadata(self) -> Tuple[EmojiData, ...]:
        with self._repository as repo:
            raw_data = repo.get_all_raw_emojis()
            return tuple(EmojiData.from_dict(raw) for raw in raw_data.values())

    def _get_available_raw_combinations_for_codepoint(self, codepoint: str) -> dict:
        with self._repository as repo:
            first_raw_emoji = repo.get_raw_emoji(codepoint)
            if first_raw_emoji is None:
                return {}
            return first_raw_emoji.get("combinations", {})

    def _populate_repository(self):
        with self._repository as repo:
            logger.info("Populating emoji repository with data from source")
            populator = EmojiDataPopulator(repository=repo)
            populator.populate_repository()
