import logging
import threading
from typing import Any

from src.core.emoji.dto.combination_data import CombinationData
from src.core.emoji.dto.emoji_couple import EmojiDataCouple
from src.core.emoji.dto.emoji_category_data import EmojiCategoryData
from src.core.emoji.dto.emoji_data import EmojiData
from src.core.emoji.emoji_data_populator import EmojiDataPopulator
from src.persistence.emoji_repository.abstract_emoji_repository import AbstractEmojiRepository

logger = logging.getLogger(__name__)


class EmojiKitchenService:
    def __init__(self, repository: AbstractEmojiRepository):
        self._repository = repository
        self._cache_lock = threading.Lock()
        self._emoji_by_codepoint: dict[str, EmojiData] = {}
        self._available_targets_by_codepoint: dict[str, tuple[str, ...]] = {}
        self._combination_by_pair: dict[tuple[str, str], dict[str, str]] = {}
        self._supported_codepoints: tuple[str, ...] = ()
        self._supported_metadata: tuple[EmojiData, ...] = ()
        self._grouped_supported_metadata: tuple[EmojiCategoryData, ...] = ()
        self._grouped_supported_payload: tuple[dict[str, Any], ...] = ()
        self._populate_repository()
        self._refresh_cache()

    def fetch_combination_data(self,
                               first_emoji_codepoint: str,
                               second_emoji_codepoint: str) -> CombinationData:
        logger.info("Fetching combination for codepoints: %s and %s", first_emoji_codepoint, second_emoji_codepoint)
        first_emoji = self.fetch_emoji_by_codepoint(first_emoji_codepoint)
        second_emoji = self.fetch_emoji_by_codepoint(second_emoji_codepoint)

        pair_key = self._pair_key(first_emoji_codepoint, second_emoji_codepoint)
        with self._cache_lock:
            raw_combination = self._combination_by_pair.get(pair_key)
        if raw_combination is None:
            raise ValueError(
                f"No combination found in emoji repository for codepoints: {first_emoji_codepoint} and {second_emoji_codepoint}"
            )

        return CombinationData(
            emoji_couple=EmojiDataCouple(first_emoji, second_emoji),
            result_image_url=raw_combination["resultImageUrl"],
            name=raw_combination["name"]
        )

    def fetch_available_codepoints_for_combination(self, reference_codepoint: str) -> tuple[str, ...]:
        with self._cache_lock:
            return self._available_targets_by_codepoint.get(reference_codepoint, ())

    def fetch_emoji_by_codepoint(self, codepoint: str) -> EmojiData:
        with self._cache_lock:
            emoji = self._emoji_by_codepoint.get(codepoint)
        if emoji is None:
            raise ValueError(f"Could not fetch emoji with codepoint '{codepoint}'")
        return emoji

    def fetch_all_supported_emoji_codepoints(self) -> tuple[str, ...]:
        with self._cache_lock:
            return self._supported_codepoints

    def fetch_all_supported_emoji_metadata(self) -> tuple[EmojiData, ...]:
        with self._cache_lock:
            return self._supported_metadata

    def fetch_grouped_supported_emoji_metadata(self) -> tuple[EmojiCategoryData, ...]:
        with self._cache_lock:
            return self._grouped_supported_metadata

    def fetch_grouped_supported_emoji_payload(self) -> tuple[dict[str, Any], ...]:
        with self._cache_lock:
            return self._grouped_supported_payload

    @staticmethod
    def _pair_key(first_codepoint: str, second_codepoint: str) -> tuple[str, str]:
        if first_codepoint <= second_codepoint:
            return first_codepoint, second_codepoint
        return second_codepoint, first_codepoint

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
            if repo.get_all_raw_emojis():
                logger.info("Emoji repository already populated, skipping remote metadata fetch")
                return
            logger.info("Populating emoji repository with data from source")
            populator = EmojiDataPopulator(repository=repo)
            populator.populate_repository()

    def _refresh_cache(self) -> None:
        with self._repository as repo:
            raw_data = repo.get_all_raw_emojis()

        emoji_by_codepoint: dict[str, EmojiData] = {}
        available_targets_by_codepoint: dict[str, tuple[str, ...]] = {}
        combination_by_pair: dict[tuple[str, str], dict[str, str]] = {}

        for codepoint, raw_emoji in raw_data.items():
            emoji_by_codepoint[codepoint] = EmojiData.from_dict(raw_emoji)

        for codepoint, raw_emoji in raw_data.items():
            raw_combinations = raw_emoji.get("combinations", {})
            available_targets_by_codepoint[codepoint] = tuple(raw_combinations.keys())
            for target_codepoint, raw_combination in raw_combinations.items():
                if not raw_combination:
                    continue
                pair_key = self._pair_key(codepoint, target_codepoint)
                combination_by_pair.setdefault(
                    pair_key,
                    {
                        "name": raw_combination["name"],
                        "resultImageUrl": raw_combination["resultImageUrl"],
                    },
                )

        supported_metadata = tuple(emoji_by_codepoint.values())
        grouped = self._group_by_category(supported_metadata)
        grouped_supported_metadata = tuple(
            EmojiCategoryData(category=category_name, emojis=tuple(category_emojis))
            for category_name, category_emojis in grouped.items()
        )
        grouped_supported_payload = tuple(category.to_dict() for category in grouped_supported_metadata)

        with self._cache_lock:
            self._emoji_by_codepoint = emoji_by_codepoint
            self._available_targets_by_codepoint = available_targets_by_codepoint
            self._combination_by_pair = combination_by_pair
            self._supported_codepoints = tuple(emoji_by_codepoint.keys())
            self._supported_metadata = supported_metadata
            self._grouped_supported_metadata = grouped_supported_metadata
            self._grouped_supported_payload = grouped_supported_payload

