from dataclasses import dataclass

from pydantic import BaseModel

from src.core.emoji.dto.emoji_couple import EmojiDataCouple
from src.core.gameplay.dto.challenge_answer import ChallengeAnswer
from src.core.gameplay.dto.guess_slot_match import GuessSlotMatch


@dataclass(frozen=True)
class ChallengeState(BaseModel):
    answer: ChallengeAnswer
    attempts: int
    max_attempts: int
    is_completed: bool
    past_guesses: tuple[EmojiDataCouple, ...]
    past_guess_matches: tuple[GuessSlotMatch, ...] = ()
