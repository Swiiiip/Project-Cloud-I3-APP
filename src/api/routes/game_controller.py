from typing import Union

from src.persistence.file_emoji_repository import FileEmojiRepository
from src.api.routes.missing_game_payload import MissingGamePayload
from src.core.service.emoji_kitchen_service import EmojiKitchenService
from src.core.gameplay.mode.daily_challenge_mode import DailyChallengeMode
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_end_result import DailyChallengeEndResult
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_guess_result import DailyChallengeGuessResult
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_start_result import DailyChallengeStartResult
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_status_result import DailyChallengeStatusResult
from src.core.gameplay.mode.endless_mode import EndlessMode
from src.core.gameplay.mode.endless_mode_results.endless_mode_end_result import EndlessModeEndResult
from src.core.gameplay.mode.endless_mode_results.endless_mode_guess_result import EndlessModeGuessResult
from src.core.gameplay.mode.endless_mode_results.endless_mode_start_result import EndlessModeStartResult
from src.core.gameplay.mode.endless_mode_results.endless_mode_status_result import EndlessModeStatusResult
from src.core.gameplay.state.daily_challenge_state import DailyChallengeState
from src.core.gameplay.state.endless_mode_state import EndlessModeState
from src.utils.path_handler import PathHandler


class GameController:
    def __init__(self):
        self.emoji_service = EmojiKitchenService(db=FileEmojiRepository(cache_path=PathHandler.cache_dir()))
        self.games: dict[str, Union[DailyChallengeMode, EndlessMode]] = {}

    def create_daily_challenge(self, game_id: str) -> DailyChallengeStartResult:
        game_state = DailyChallengeState(game_id)
        game_mode = DailyChallengeMode(game_state, self.emoji_service.supported_emoji_codes)
        self.games[game_id] = game_mode
        return game_mode.start_game()

    def create_endless_game(self, game_id: str) -> EndlessModeStartResult:
        game_state = EndlessModeState(game_id)
        game_mode = EndlessMode(game_state, self.emoji_service.supported_emoji_codes)
        self.games[game_id] = game_mode
        return game_mode.start_game()

    def make_guess(
        self, game_id: str, guess: str
    ) -> Union[DailyChallengeGuessResult, EndlessModeGuessResult, MissingGamePayload]:
        if game_id not in self.games:
            return MissingGamePayload(error="Game not found")
        return self.games[game_id].make_guess(guess)

    def get_game_status(
        self, game_id: str
    ) -> Union[
        DailyChallengeStatusResult, EndlessModeStatusResult, MissingGamePayload
    ]:
        if game_id not in self.games:
            return MissingGamePayload(error="Game not found")
        return self.games[game_id].get_game_status()

    def end_game(
        self, game_id: str
    ) -> Union[DailyChallengeEndResult, EndlessModeEndResult, MissingGamePayload]:
        if game_id not in self.games:
            return MissingGamePayload(error="Game not found")
        result = self.games[game_id].end_game()
        del self.games[game_id]
        return result
