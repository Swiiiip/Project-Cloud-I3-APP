import logging

from typing import Any

import requests

from src.core.emoji.dto.combination_data import CombinationData
from src.core.emoji.dto.emoji_couple import EmojiDataCouple
from src.core.emoji.dto.emoji_data import EmojiData
from src.core.emoji.dto.unit_data import UnitData
from src.persistence.emoji_repository.abstract_emoji_repository import AbstractEmojiRepository
from src.utils.runtime_env import RuntimeEnv

logger = logging.getLogger(__name__)
UNKNOWN_TAXONOMY_LABEL = "Unknown"


class EmojiDataPopulator:
    def __init__(self, repository: AbstractEmojiRepository):
        self._repository = repository

    def populate_repository(self):
        raw_metadata = self._fetch_raw_emoji_kitchen_metadata()
        logger.info("Fetched raw metadata with %d emoji entries", len(raw_metadata))
        unit_collection = self._to_unit_data_collection(raw_metadata)

        with self._repository:
            for unit in unit_collection:
                self._register_emoji(unit.reference_emoji)
                for combination in unit.combinations:
                    self._register_combination(combination)

    def _register_combination(self, combination: CombinationData):
        first_emoji = combination.emoji_couple.first_emoji
        second_emoji = combination.emoji_couple.second_emoji
        self._register_emoji(first_emoji)
        self._register_emoji(second_emoji)

        payload = combination.to_dict()

        self._repository.update_combination_entry(first_emoji.codepoint, second_emoji.codepoint, payload)
        self._repository.update_combination_entry(second_emoji.codepoint, first_emoji.codepoint, payload)

    def _register_emoji(self, emoji: EmojiData):
        self._repository.save_raw_emoji(emoji.codepoint, emoji.to_dict())

    @staticmethod
    def _fetch_raw_emoji_kitchen_metadata() -> dict[str, Any]:
        response = requests.get(url=RuntimeEnv.require_str("EMOJI_KITCHEN_METADATA_URL"),
                                timeout=RuntimeEnv.require_int("INTERNAL_HTTP_TIMEOUT_SECONDS"))
        response.raise_for_status()
        full_json = response.json()
        return full_json.get("data", {})

    def _to_unit_data_collection(self, raw_data: dict[str, Any]) -> tuple[UnitData, ...]:
        units = []
        emoji_map = self._create_emoji_map(raw_data)
        for codepoint, details in raw_data.items():
            raw_combinations = details.get("combinations", {})
            ref_emoji = emoji_map[codepoint]
            combinations = EmojiDataPopulator._map_combinations(emoji_map=emoji_map,
                                                                reference_emoji=ref_emoji,
                                                                raw_combinations=raw_combinations)
            units.append(UnitData(reference_emoji=ref_emoji, combinations=combinations))
        logger.info(f"Mapped raw data to {len(units)} unit data entries")
        return tuple(units)

    def _create_emoji_map(self, raw_data: dict[str, Any]) -> dict[str, EmojiData]:
        return {codepoint: EmojiData(name=self._format_item_string(details["alt"]),
                                     character=details["emoji"],
                                     codepoint=codepoint,
                                     keyboard_position=details["gBoardOrder"],
                                     keywords=details["keywords"],
                                     category=self._format_taxonomy_label(details.get("category")),
                                     subcategory=self._format_taxonomy_label(details.get("subcategory")))
                for codepoint, details in raw_data.items()}

    @staticmethod
    def _map_combinations(emoji_map: dict[str, EmojiData],
                          reference_emoji: EmojiData,
                          raw_combinations: dict[str, Any]) -> tuple[CombinationData, ...]:
        combinations = []
        for target_codepoint, combination_list in raw_combinations.items():
            if target_codepoint in emoji_map and combination_list:
                first_combination_info = combination_list[0]
                couple = EmojiDataCouple(first_emoji=reference_emoji,
                                         second_emoji=emoji_map[target_codepoint])
                combinations.append(CombinationData(
                    name=first_combination_info.get("alt"),
                    result_image_url=first_combination_info.get("gStaticUrl"),
                    emoji_couple=couple
                ))
        logger.debug(f"Mapped {len(combinations)} combinations for codepoint {reference_emoji.codepoint}")
        return tuple(combinations)

    @staticmethod
    def _format_item_string(text) -> str:
        words = text.split("_")
        formatted_words = []
        for word in words:
            if word == "and":
                formatted_words.append("&")
            else:
                formatted_words.append(word)

        sentence = " ".join(formatted_words)
        return sentence.capitalize()

    @staticmethod
    def _format_taxonomy_label(text: str | None) -> str:
        if text is None or text.strip() == "":
            return UNKNOWN_TAXONOMY_LABEL
        return EmojiDataPopulator._format_item_string(text)

