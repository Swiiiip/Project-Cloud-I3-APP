from dataclasses import dataclass

from pydantic import BaseModel

from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple


@dataclass(frozen=True)
class ChallengeAnswer(BaseModel):
    name: str
    result_image_url: str
    emoji_codepoint_couple: EmojiCodepointCouple
