from dataclasses import dataclass

from pydantic import BaseModel

from src.core.emoji.dto.emoji_data import EmojiData


@dataclass(frozen=True)
class EmojiDataCouple(BaseModel):
    first_emoji: EmojiData
    second_emoji: EmojiData


@dataclass(frozen=True)
class EmojiCodepointCouple(BaseModel):
    first_emoji_codepoint: str
    second_emoji_codepoint: str
