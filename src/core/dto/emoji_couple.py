from dataclasses import dataclass

from src.core.dto.emoji_data import EmojiData


@dataclass(frozen=True)
class EmojiCouple:
    first_emoji: EmojiData
    second_emoji: EmojiData
