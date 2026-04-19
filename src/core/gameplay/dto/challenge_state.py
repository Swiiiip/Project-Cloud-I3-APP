from dataclasses import dataclass
from typing import Tuple

from pydantic import BaseModel

from src.core.emoji.dto.emoji_couple import EmojiDataCouple
from src.core.gameplay.dto.challenge_answer import ChallengeAnswer


@dataclass(frozen=True)
class ChallengeState(BaseModel):
    answer: ChallengeAnswer
    attempts: int
    max_attempts: int
    is_completed: bool
    past_guesses: Tuple[EmojiDataCouple, ...]
