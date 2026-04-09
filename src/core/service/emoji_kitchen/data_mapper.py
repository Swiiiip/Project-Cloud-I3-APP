import logging
from typing import Dict, Any, Tuple

from src.core.dto.combination_data import CombinationData
from src.core.dto.emoji_data import EmojiData
from src.core.dto.unit_data import UnitData


logger = logging.getLogger(__name__)


class EmojiKitchenDataMapper:
    @classmethod
    def to_unit_data_collection(cls, raw_data: Dict[str, Any]) -> Tuple[UnitData, ...]:
        units = []
        emoji_map = cls._create_emoji_map(raw_data)
        for codepoint, details in raw_data.items():
            raw_combinations = details.get("combinations", {})
            ref_emoji = emoji_map[codepoint]
            combinations = cls._map_combinations(emoji_map=emoji_map,
                                                 reference_emoji=ref_emoji,
                                                 raw_combinations=raw_combinations)
            units.append(UnitData(reference_emoji=ref_emoji, combinations=combinations))
        logger.info(f"Mapped raw data to {len(units)} unit data entries")
        return tuple(units)

    @classmethod
    def _create_emoji_map(cls,
                          raw_data: Dict[str, Any]) -> Dict[str, EmojiData]:
        return {codepoint: EmojiData(name=details["alt"],
                              character=details["emoji"],
                              codepoint=codepoint,
                              keyboard_position=details["gBoardOrder"],
                              keywords=details["keywords"],
                              category=details["category"],
                              subcategory=details["subcategory"])
                for codepoint, details in raw_data.items()}

    @classmethod
    def _map_combinations(cls,
                          emoji_map: Dict[str, EmojiData],
                          reference_emoji: EmojiData,
                          raw_combinations: Dict[str, Any]) -> Tuple[CombinationData, ...]:
        combinations = []
        for target_codepoint, combination_list in raw_combinations.items():
            if target_codepoint in emoji_map and combination_list:
                first_combination_info = combination_list[0]
                combinations.append(CombinationData(
                    name=first_combination_info.get("alt"),
                    result_image_url=first_combination_info.get("gStaticUrl"),
                    first_emoji=reference_emoji,
                    second_emoji=emoji_map[target_codepoint]
                ))
        return tuple(combinations)
