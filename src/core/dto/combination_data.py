from dataclasses import dataclass
from typing import Dict, Any

from src.core.dto.emoji_data import EmojiData


@dataclass(frozen=True)
class CombinationData:
    name: str
    result_image_url: str
    first_emoji: EmojiData
    second_emoji: EmojiData

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "resultImageUrl": self.result_image_url
        }
