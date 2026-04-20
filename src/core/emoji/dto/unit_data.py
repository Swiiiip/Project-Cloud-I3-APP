from dataclasses import dataclass

from typing import Any

from src.core.emoji.dto.combination_data import CombinationData
from src.core.emoji.dto.emoji_data import EmojiData


@dataclass(frozen=True)
class UnitData:
    reference_emoji: EmojiData
    combinations: tuple[CombinationData, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.reference_emoji.name,
                "character": self.reference_emoji.character,
                "codepoint": self.reference_emoji.codepoint,
                "keyboardPosition": self.reference_emoji.keyboard_position,
                "keywords": self.reference_emoji.keywords,
                "category": self.reference_emoji.category,
                "subcategory": self.reference_emoji.subcategory,
                "combinations": tuple(combo.to_dict() for combo in self.combinations)}
