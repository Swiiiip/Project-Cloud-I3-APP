from dataclasses import dataclass
from typing import Dict, Any

from src.core.emoji.dto.emoji_couple import EmojiCouple


@dataclass(frozen=True)
class CombinationData:
    name: str
    result_image_url: str
    emoji_couple: EmojiCouple

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "resultImageUrl": self.result_image_url
        }
