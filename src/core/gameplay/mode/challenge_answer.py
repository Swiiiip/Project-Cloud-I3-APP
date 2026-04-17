from dataclasses import dataclass

from src.core.emoji.dto.emoji_couple import EmojiCouple


@dataclass(frozen=True)
class ChallengeAnswer:
    name: str
    result_image_url: str
    emoji_couple: EmojiCouple
