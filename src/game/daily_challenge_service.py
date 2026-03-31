import random
from datetime import datetime, timezone
from src.config.config import Config
from src.dtos.daily_challenge_state import DailyChallengeState
from src.dtos.guess_attempt import GuessAttempt
from src.dtos.error_response import error_response
from src.storage.abstract_game_state_store import AbstractGameStateStore
from src.core.emoji_kitchen_service import EmojiKitchenService


class DailyChallengeService:
    def __init__(self, config: Config, emoji_service: EmojiKitchenService, store: AbstractGameStateStore):
        self.config = config
        self.emoji_service = emoji_service
        self.store = store

    def _get_today_date_str(self) -> str:
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%d")

    def _get_random_emojis(self) -> list[str]:
        return self.emoji_service.get_random_combination()

    def start_daily_challenge(self, user_id: str) -> dict:
        today_date = self._get_today_date_str()

        if self.store.exists_daily_challenge(user_id, today_date):
            existing = self.store.load_daily_challenge(user_id, today_date)
            if existing and not existing.is_completed:
                return {
                    "message": "Challenge already started for today",
                    "state": existing.to_dict()
                }
            # If not existing or completed, fall through to start a new one

        target_emojis = self._get_random_emojis()
        if target_emojis is None:
            return error_response("Failed to generate random combination.")
        now = datetime.now(timezone.utc)

        state = DailyChallengeState(
            challenge_date=today_date,
            target_emojis=target_emojis,
            guesses=[],
            remaining_attempts=self.config.daily_challenge_max_guesses,
            is_completed=False,
            is_won=False,
            created_at=now
        )

        self.store.save_daily_challenge(user_id, state)
        return {
            "message": "Daily challenge started",
            "state": state.to_dict()
        }

    def make_guess(self, user_id: str, guessed_emojis: list[str]) -> dict:
        today_date = self._get_today_date_str()
        state = self.store.load_daily_challenge(user_id, today_date)

        if not state:
            return error_response("No active daily challenge for today. Start a new one with start_daily_challenge().")

        if state.is_completed:
            return error_response("Daily challenge already completed.")

        for emoji in guessed_emojis:
            if not self.emoji_service.is_supported(self.emoji_service._get_codepoint(emoji)):
                return error_response(f"Emoji {emoji} is not supported.")

        is_correct = set(guessed_emojis) == set(state.target_emojis)
        now = datetime.now(timezone.utc)

        attempt = GuessAttempt(
            emojis=guessed_emojis,
            timestamp=now,
            is_correct=is_correct
        )

        state.guesses.append(attempt)
        state.remaining_attempts -= 1

        if is_correct:
            state.is_completed = True
            state.is_won = True
            state.completed_at = now
        elif state.remaining_attempts == 0:
            state.is_completed = True
            state.is_won = False
            state.completed_at = now

        self.store.save_daily_challenge(user_id, state)

        return {
            "is_correct": is_correct,
            "state": state.to_dict()
        }

    def get_challenge_state(self, user_id: str) -> dict:
        today_date = self._get_today_date_str()
        state = self.store.load_daily_challenge(user_id, today_date)

        if not state:
            return error_response("No active daily challenge for today.")

        return {"state": state.to_dict()}
