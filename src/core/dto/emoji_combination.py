from dataclasses import asdict, dataclass
from typing import Dict, Any

from core.dto.emoji_data import EmojiData


@dataclass(frozen=True)
class EmojiCombination:
    first_emoji: EmojiData
    second_emoji: EmojiData
    result_emoji: EmojiData
    result_image_bytes: bytes

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_json_dict(data: Dict[str, Any]):
        return EmojiCombination(
            first_emoji=EmojiData(**data["first_emoji"]),
            second_emoji=EmojiData(**data["second_emoji"]),
            result_emoji=EmojiData(**data["result_emoji"]),
            result_image_bytes=data["result_image_bytes"]
        )
