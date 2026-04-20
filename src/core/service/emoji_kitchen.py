import logging

from src.core.emoji.dto.combination_data import CombinationData
from src.core.emoji.dto.emoji_couple import EmojiDataCouple
from src.core.emoji.dto.emoji_category_data import EmojiCategoryData
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

    def fetch_available_codepoints_for_combination(self, reference_codepoint: str) -> tuple[str, ...]:
        raw_combinations = self._get_available_raw_combinations_for_codepoint(reference_codepoint)
        return tuple(raw_combinations.keys())

    def fetch_emoji_by_codepoint(self, codepoint: str) -> EmojiData:
        with self._repository as repo:
            raw_emoji = repo.get_raw_emoji(codepoint)
            if not raw_emoji:
                raise ValueError(f"Could not fetch emoji with codepoint '{codepoint}'")
            return EmojiData.from_dict(raw_emoji)

    def fetch_all_supported_emoji_codepoints(self) -> tuple[str, ...]:
        with self._repository as repo:
            raw_data = repo.get_all_raw_emojis()
            return tuple(raw["codepoint"] for raw in raw_data.values())

    def fetch_all_supported_emoji_metadata(self) -> tuple[EmojiData, ...]:
        with self._repository as repo:
            raw_data = repo.get_all_raw_emojis()
            return tuple(EmojiData.from_dict(raw) for raw in raw_data.values())

    def fetch_grouped_supported_emoji_metadata(self) -> tuple[EmojiCategoryData, ...]:
        emojis = self.fetch_all_supported_emoji_metadata()
        grouped_emojis = self._group_by_category(emojis)
        return tuple(
            EmojiCategoryData(category=category_name, emojis=tuple(category_emojis))
            for category_name, category_emojis in grouped_emojis.items()
        )

    def _get_available_raw_combinations_for_codepoint(self, codepoint: str) -> dict:
        with self._repository as repo:
            first_raw_emoji = repo.get_raw_emoji(codepoint)
            if first_raw_emoji is None:
                return {}
            return first_raw_emoji.get("combinations", {})

    @staticmethod
    def _group_by_category(emojis: tuple[EmojiData, ...]) -> dict[str, list[EmojiData]]:
        grouped: dict[str, list[EmojiData]] = {}
        for emoji in sorted(emojis, key=EmojiKitchenService._sort_emoji_key):
            grouped.setdefault(emoji.category, []).append(emoji)

        return dict(sorted(grouped.items(), key=lambda item: item[0].casefold()))

    @staticmethod
    def _sort_emoji_key(emoji: EmojiData) -> tuple[str, int, str]:
        return (
            emoji.category,
            emoji.keyboard_position,
            emoji.name,
        )

    def _populate_repository(self):
        with self._repository as repo:
            logger.info("Populating emoji repository with data from source")
            populator = EmojiDataPopulator(repository=repo)
            populator.populate_repository()
