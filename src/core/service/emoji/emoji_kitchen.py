import logging
from typing import Tuple, Optional

from src.core.dto.combination_data import CombinationData
from src.core.dto.emoji_couple import EmojiCouple
from src.core.dto.emoji_data import EmojiData
from src.persistence.abstract_emoji_repository import AbstractEmojiRepository
from src.persistence.file_emoji_repository import FileEmojiRepository

logger = logging.getLogger(__name__)


class EmojiKitchenService:
    def __init__(self, repository: AbstractEmojiRepository):
        self._repository = repository

    def fetch_combination(self,
                          first_emoji_codepoint: str,
                          second_emoji_codepoint: str) -> Optional[CombinationData]:
        logger.info("Fetching combination for codepoints: %s and %s", first_emoji_codepoint, second_emoji_codepoint)
        first_emoji = self.fetch_emoji_by_codepoint(first_emoji_codepoint)
        second_emoji = self.fetch_emoji_by_codepoint(second_emoji_codepoint)

        if not first_emoji or not second_emoji:
            return None

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
            emoji_couple=EmojiCouple(first_emoji, second_emoji),
            result_image_url=raw_combination["resultImageUrl"],
            name=raw_combination.get("name", "")
        )

    def fetch_available_codepoints_for_combination(self, reference_codepoint: str) -> Tuple[str]:
        raw_combinations = self._get_available_raw_combinations_for_codepoint(reference_codepoint)
        return tuple(raw_combinations.keys())

    def fetch_emoji_by_codepoint(self, codepoint: str) -> Optional[EmojiData]:
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


if __name__ == "__main__":
    from src.core.service.emoji.emoji_data_population import EmojiDataPopulationService
    from src.utils.logger_coonfigurator import LoggerConfigurator
    from src.utils.path_handler import PathHandler

    LoggerConfigurator.config_logger()
    emoji_repository = FileEmojiRepository(storage_path=PathHandler.root_dir() / "test_cache.json")

    with emoji_repository:
        service = EmojiKitchenService(emoji_repository)
        populator = EmojiDataPopulationService(repository=emoji_repository)
        # populator.populate_repository()
        combo = service.fetch_combination("1f36a", "1f36a")

        if combo:
            print(f"Match found: {combo.name}")
            print(f"Image: {combo.result_image_url}")
            print(f"Left Side: {combo.emoji_couple.first_emoji.character}")
            print(f"Right Side: {combo.emoji_couple.second_emoji.character}")
