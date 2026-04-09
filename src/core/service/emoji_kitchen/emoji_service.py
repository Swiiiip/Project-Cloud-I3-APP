import logging
from typing import Tuple, Optional, Dict, Any

import requests

from src.config import Config
from src.core.dto.combination_data import CombinationData
from src.core.dto.emoji_data import EmojiData
from src.core.service.emoji_kitchen.data_mapper import EmojiKitchenDataMapper
from src.persistence.abstract_emoji_repository import AbstractEmojiRepository
from src.persistence.file_emoji_repository import FileEmojiRepository
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler

logger = logging.getLogger(__name__)


class EmojiKitchenService:
    def __init__(self, repository: AbstractEmojiRepository):
        self._repository = repository

    def populate_repository(self):
        raw_metadata = self._fetch_raw_metadata()
        logger.info("Fetched raw metadata with %d emoji entries", len(raw_metadata))
        unit_collection = EmojiKitchenDataMapper.to_unit_data_collection(raw_metadata)

        with self._repository:
            for unit in unit_collection:
                self.register_emoji(unit.reference_emoji)
                for combination in unit.combinations:
                    self.register_combination(combination)

    def fetch_combination(self,
                          first_emoji_codepoint: str,
                          second_emoji_codepoint: str) -> Optional[CombinationData]:
        first_emoji = self.fetch_emoji_by_codepoint(first_emoji_codepoint)
        second_emoji = self.fetch_emoji_by_codepoint(second_emoji_codepoint)

        if not first_emoji or not second_emoji:
            return None

        raw_source = self._repository.get_raw_emoji(first_emoji_codepoint)
        if raw_source is None:
            return None
        raw_combination = raw_source.get("combinations", {}).get(second_emoji_codepoint)

        if not raw_combination:
            return None

        return CombinationData(
            first_emoji=first_emoji,
            second_emoji=second_emoji,
            result_image_url=raw_combination.get("resultImageUrl"),
            name=raw_combination.get("name")
        )

    def fetch_emoji_by_codepoint(self, codepoint: str) -> Optional[EmojiData]:
        raw_emoji = self._repository.get_raw_emoji(codepoint)
        if not raw_emoji:
            return None
        return EmojiData.from_dict(raw_emoji)

    def fetch_all_supported_emojis(self) -> Tuple[EmojiData, ...]:
        raw_data = self._repository.get_all_raw_emojis()
        return tuple(EmojiData.from_dict(raw) for raw in raw_data.values())

    def register_emoji(self, emoji: EmojiData):
        self._repository.save_raw_emoji(emoji.codepoint, emoji.to_dict())

    def register_combination(self, combination: CombinationData):
        self.register_emoji(combination.first_emoji)
        self.register_emoji(combination.second_emoji)

        codepoint1 = combination.first_emoji.codepoint
        codepoint2 = combination.second_emoji.codepoint
        payload = combination.to_dict()

        self._repository.update_combination_entry(codepoint1, codepoint2, payload)
        self._repository.update_combination_entry(codepoint2, codepoint1, payload)

    @staticmethod
    def _fetch_raw_metadata() -> Dict[str, Any]:
        response = requests.get(url=Config.EMOJI_KITCHEN_METADATA_URL,
                                timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status()
        full_json = response.json()
        return full_json.get("data", {})


if __name__ == "__main__":
    LoggerConfigurator.config_logger()
    emoji_repository = FileEmojiRepository(storage_path=PathHandler.root_dir() / "test_cache.json")

    with emoji_repository:
        service = EmojiKitchenService(emoji_repository)
        service.populate_repository()
        combo = service.fetch_combination("2615", "2665-fe0f")

        if combo:
            print(f"Match found: {combo.name}")
            print(f"Image: {combo.result_image_url}")
            print(f"Left Side: {combo.first_emoji.character}")
            print(f"Right Side: {combo.second_emoji.character}")
