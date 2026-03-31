from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DailyChallengeState:
    challenge_date: str
    target_emojis: list[str]
    guesses: list
    remaining_attempts: int
    is_completed: bool
    is_won: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "challenge_date": self.challenge_date,
            "target_emojis": self.target_emojis,
            "guesses": [
                {
                    "emojis": g.emojis,
                    "timestamp": g.timestamp.isoformat(),
                    "is_correct": g.is_correct
                }
                for g in self.guesses
            ],
            "remaining_attempts": self.remaining_attempts,
            "is_completed": self.is_completed,
            "is_won": self.is_won,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
