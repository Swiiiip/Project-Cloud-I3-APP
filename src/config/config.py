import os
from typing import Literal


class Config:
    def __init__(self, environment: Literal["dev", "prod"] = "dev"):
        self.environment = environment
        self.emoji_kitchen_metadata_url = os.getenv(
            "EMOJI_KITCHEN_METADATA_URL",
            "https://raw.githubusercontent.com/xsalazar/emoji-kitchen-backend/main/app/metadata.json"
        )
        self.daily_challenge_max_guesses = int(os.getenv("DAILY_CHALLENGE_MAX_GUESSES", "5"))
        self.daily_reset_hour_utc = int(os.getenv("DAILY_RESET_HOUR_UTC", "0"))
        self.enable_request_timeout = float(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))
        self.game_state_dir = os.getenv("GAME_STATE_DIR", ".game_state")

    @staticmethod
    def from_environment() -> "Config":
        env = os.getenv("APP_ENV", "dev")
        return Config(environment=env)


