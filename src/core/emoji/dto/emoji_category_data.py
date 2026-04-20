from dataclasses import dataclass
from typing import Any

from src.core.emoji.dto.emoji_data import EmojiData


@dataclass(frozen=True)
class EmojiCategoryData:
    category: str
    emojis: tuple[EmojiData, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EmojiCategoryData":
        return cls(
            category=data["category"],
            emojis=tuple(EmojiData.from_dict(raw_emoji) for raw_emoji in data.get("emojis", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "emojis": [emoji.to_dict() for emoji in self.emojis],
        }
