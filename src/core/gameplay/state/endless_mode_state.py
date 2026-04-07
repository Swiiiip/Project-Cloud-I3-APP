from typing import Optional

from src.core.gameplay.state.abstract_game_state import AbstractGameState
from src.core.gameplay.state.endless_mode_state_snapshot import EndlessModeStateSnapshot


class EndlessModeState(AbstractGameState):
    def __init__(self, game_id: str):
        super().__init__(game_id)
        self.streak = 0
        self.max_streak = 0
        self.current_emoji: Optional[str] = None

    def to_snapshot(self) -> EndlessModeStateSnapshot:
        return EndlessModeStateSnapshot(
            game_id=self.game_id,
            score=self.score,
            attempts=self.attempts,
            is_completed=self.is_completed,
            streak=self.streak,
            max_streak=self.max_streak,
            current_emoji=self.current_emoji,
        )

    def update_score(self, points: int) -> None:
        self.score += points
        self.streak += 1
        if self.streak > self.max_streak:
            self.max_streak = self.streak

    def increment_attempts(self) -> None:
        self.attempts += 1

    def complete_game(self) -> None:
        self.is_completed = True

    def reset_streak(self) -> None:
        self.streak = 0

    def set_current_emoji(self, emoji: str) -> None:
        self.current_emoji = emoji
