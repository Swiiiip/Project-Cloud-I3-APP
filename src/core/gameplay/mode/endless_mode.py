import random
from typing import List

from src.core.gameplay.mode.endless_mode_results.endless_mode_end_result import EndlessModeEndResult
from src.core.gameplay.mode.endless_mode_results.endless_mode_guess_correct import EndlessModeGuessCorrect
from src.core.gameplay.mode.endless_mode_results.endless_mode_guess_result import EndlessModeGuessResult
from src.core.gameplay.mode.endless_mode_results.endless_mode_guess_wrong import EndlessModeGuessWrong
from src.core.gameplay.mode.endless_mode_results.endless_mode_start_result import EndlessModeStartResult
from src.core.gameplay.mode.endless_mode_results.endless_mode_status_result import EndlessModeStatusResult
from src.core.gameplay.mode.abstract_endless_mode import AbstractEndlessMode
from src.core.service.emoji_kitchen_service import EmojiKitchenService
from src.core.gameplay.state.endless_mode_state import EndlessModeState


class EndlessMode(AbstractEndlessMode):
    def __init__(self, game_state: EndlessModeState, emoji_service: EmojiKitchenService):
        super().__init__(game_state)
        self.emoji_service = emoji_service
        self.available_emojis: List[str] = [
            "🎯", "☕", "👻", "🔥", "💎", "🌟", "🎨", "🎪", "🎭", "🌈"
        ]

    def start_game(self) -> EndlessModeStartResult:
        self._set_new_emoji()
        return EndlessModeStartResult(
            status="started",
            game_id=self.game_state.game_id,
            current_emoji=self.game_state.current_emoji,
        )

    def make_guess(self, guess: str) -> EndlessModeGuessResult:
        self.game_state.increment_attempts()

        if guess == self.game_state.current_emoji:
            self.game_state.update_score(10)
            self._set_new_emoji()
            return EndlessModeGuessCorrect(
                correct=True,
                score=self.game_state.score,
                streak=self.game_state.streak,
                next_emoji=self.game_state.current_emoji,
            )
        self.game_state.reset_streak()
        return EndlessModeGuessWrong(
            correct=False,
            score=self.game_state.score,
            streak=self.game_state.streak,
            current_emoji=self.game_state.current_emoji,
        )

    def get_game_status(self) -> EndlessModeStatusResult:
        return EndlessModeStatusResult(
            game_id=self.game_state.game_id,
            score=self.game_state.score,
            attempts=self.game_state.attempts,
            streak=self.game_state.streak,
            max_streak=self.game_state.max_streak,
            current_emoji=self.game_state.current_emoji,
        )

    def end_game(self) -> EndlessModeEndResult:
        self.game_state.complete_game()
        return EndlessModeEndResult(
            status="ended",
            final_score=self.game_state.score,
            max_streak=self.game_state.max_streak,
            total_attempts=self.game_state.attempts,
        )

    def _set_new_emoji(self) -> None:
        self.game_state.set_current_emoji(random.choice(self.available_emojis))
