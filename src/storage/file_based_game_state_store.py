from datetime import datetime
from pathlib import Path
import json
from src.storage.abstract_game_state_store import AbstractGameStateStore
from src.config.config import Config
from src.dtos.daily_challenge_state import DailyChallengeState
from src.dtos.guess_attempt import GuessAttempt


class FileBasedGameStateStore(AbstractGameStateStore):
    def __init__(self, config: Config):
        self.storage_dir = Path(config.game_state_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def _get_file_path(self, user_id: str, challenge_date: str) -> Path:
        return self.storage_dir / f"daily_challenge_{user_id}_{challenge_date}.json"

    def save_daily_challenge(self, user_id: str, state: DailyChallengeState) -> None:
        file_path = self._get_file_path(user_id, state.challenge_date)
        with open(file_path, "w") as f:
            json.dump(state.to_dict(), f, indent=2)

    def load_daily_challenge(self, user_id: str, challenge_date: str) -> DailyChallengeState | None:
        file_path = self._get_file_path(user_id, challenge_date)
        if not file_path.exists():
            return None

        with open(file_path, "r") as f:
            data = json.load(f)

        guesses = [
            GuessAttempt(
                emojis=g["emojis"],
                timestamp=datetime.fromisoformat(g["timestamp"]),
                is_correct=g["is_correct"]
            )
            for g in data.get("guesses", [])
        ]

        return DailyChallengeState(
            challenge_date=data["challenge_date"],
            target_emojis=data["target_emojis"],
            guesses=guesses,
            remaining_attempts=data["remaining_attempts"],
            is_completed=data["is_completed"],
            is_won=data["is_won"],
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        )

    def exists_daily_challenge(self, user_id: str, challenge_date: str) -> bool:
        return self._get_file_path(user_id, challenge_date).exists()
