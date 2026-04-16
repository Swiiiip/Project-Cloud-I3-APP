import logging
import random
from datetime import date
from typing import Dict

from src.config import Config
from src.core.dto.combination_data import CombinationData
from src.core.gameplay.mode.challenge_answer import ChallengeAnswer
from src.core.gameplay.mode.challenge_state import ChallengeState
from src.core.service.emoji.emoji_kitchen import EmojiKitchenService

logger = logging.Logger(__name__)


class DailyChallengeService:
    _max_combination_retries = 3

    def __init__(self, emoji_service: EmojiKitchenService):
        self._emoji_service = emoji_service
        self._sessions: Dict[str, ChallengeState] = {}

    def get_user_state(self, user_id: str) -> ChallengeState:
        if user_id not in self._sessions:
            daily_combination = self._pick_daily_combination()
            daily_answer = ChallengeAnswer(name=daily_combination.name,
                                           emoji_couple=daily_combination.emoji_couple,
                                           result_image_url=daily_combination.result_image_url)
            self._sessions[user_id] = ChallengeState(answer=daily_answer,
                                                     attempts=0,
                                                     max_attempts=Config.DAILY_CHALLENGE_MAX_GUESSES,
                                                     is_completed=False)
        return self._sessions[user_id]

    def process_guess(self, user_id: str, first_codepoint_guess: str, second_codepoint_guess: str) -> ChallengeState:
        state = self.get_user_state(user_id)
        if state.is_completed:
            return state
        answer_emoji_couple = state.answer.emoji_couple
        is_correct_guess = (first_codepoint_guess == answer_emoji_couple.first_emoji.codepoint
                            and
                            second_codepoint_guess == answer_emoji_couple.second_emoji.codepoint)
        if is_correct_guess:
            state = state.solve()
        else:
            state = state.increment_attempt()
        self._sessions[user_id] = state
        return state

    def _pick_daily_combination(self) -> CombinationData:
        emojis = self._emoji_service.fetch_all_supported_emoji_codepoints()
        random.seed(int(date.today().strftime("%Y%m%d")))

        for _ in range(self._max_combination_retries):
            first_codepoint = random.choice(emojis)
            available_combinations = self._emoji_service.fetch_available_codepoints_for_combination(first_codepoint)
            second_codepoint = random.choice(available_combinations)

            combination = self._emoji_service.fetch_combination(first_codepoint, second_codepoint)
            if combination is not None:
                logger.info(f"Daily emoji couple to guess : {combination.emoji_couple}")
                return combination
        raise ValueError(f"No combination could be found after {self._max_combination_retries} retries.")


if __name__ == '__main__':
    from src.utils.logger_coonfigurator import LoggerConfigurator
    from src.utils.path_handler import PathHandler
    from src.persistence.file_emoji_repository import FileEmojiRepository
    from src.core.service.emoji.emoji_data_population import EmojiDataPopulationService

    LoggerConfigurator.config_logger()
    emoji_repository = FileEmojiRepository(PathHandler.src_dir / "emojis.json")
    with emoji_repository as repo:
        populator = EmojiDataPopulationService(repo)
        populator.populate_repository()
        emoji_service = EmojiKitchenService(repo)
        game_service = DailyChallengeService(emoji_service)

        user_id = "test_user"
        state = game_service.get_user_state(user_id)

        guess_state = game_service.process_guess(user_id, "u1f600", "u1f600")
        print(guess_state)
