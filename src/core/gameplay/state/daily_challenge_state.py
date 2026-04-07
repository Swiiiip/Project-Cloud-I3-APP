from datetime import date
from typing import List

from src.core.gameplay.state.abstract_game_state import AbstractGameState
from src.core.gameplay.state.daily_challenge_state_snapshot import DailyChallengeStateSnapshot


class DailyChallengeState(AbstractGameState):
    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.date = date.today()
        self.daily_emojis: List[str] = []
        self.guessed_emojis: List[str] = []

    def to_snapshot(self) -> DailyChallengeStateSnapshot:
        return DailyChallengeStateSnapshot(
            game_id=self.game_id,
            score=self.score,
            attempts=self.attempts,
            is_completed=self.is_completed,
            date=self.date,
            daily_emojis=list(self.daily_emojis),
            guessed_emojis=list(self.guessed_emojis),
        )

    def update_score(self, points: int) -> None:
        self.score += points

    def increment_attempts(self) -> None:
        self.attempts += 1

    def complete_game(self) -> None:
        self.is_completed = True

    def add_guessed_emoji(self, emoji: str) -> None:
        if emoji not in self.guessed_emojis:
            self.guessed_emojis.append(emoji)
