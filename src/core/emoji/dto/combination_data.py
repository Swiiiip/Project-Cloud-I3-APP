from dataclasses import dataclass
from typing import Any

from src.core.emoji.dto.emoji_couple import EmojiDataCouple


@dataclass(frozen=True)
class CombinationData:
    name: str
    result_image_url: str
    emoji_couple: EmojiDataCouple

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "resultImageUrl": self.result_image_url
        }
