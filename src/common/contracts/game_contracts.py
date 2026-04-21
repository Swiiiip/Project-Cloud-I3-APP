from pydantic import BaseModel

from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple


class GameGuessRequest(BaseModel):
    session_id: str
    guess: EmojiCodepointCouple

