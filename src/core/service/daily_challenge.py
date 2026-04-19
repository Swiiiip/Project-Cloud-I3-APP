import logging
import random
from datetime import date

from src.config import Config
from src.core.emoji.dto.combination_data import CombinationData
from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple, EmojiDataCouple
from src.core.emoji.dto.emoji_data import EmojiData
from src.core.gameplay.dto.challenge_answer import ChallengeAnswer
from src.core.gameplay.dto.challenge_state import ChallengeState
from src.core.service.emoji_kitchen import EmojiKitchenService
from src.persistence.abstract_challenge_storage import AbstractChallengeStorage

logger = logging.Logger(__name__)


class DailyChallengeService:
    _max_combination_retries = 3

    def __init__(self, emoji_service: EmojiKitchenService, storage: AbstractChallengeStorage):
        self._emoji_service = emoji_service
        self._storage = storage

    def get_user_state(self, user_id: str) -> ChallengeState:
        state = self._storage.get_state(user_id)

        if state is None:
            daily_combination = self._pick_daily_combination()
            emoji_codepoint_couple = EmojiCodepointCouple(
                first_emoji_codepoint=daily_combination.emoji_couple.first_emoji.codepoint,
                second_emoji_codepoint=daily_combination.emoji_couple.second_emoji.codepoint)
            daily_answer = ChallengeAnswer(name=daily_combination.name,
                                           emoji_codepoint_couple=emoji_codepoint_couple,
                                           result_image_url=daily_combination.result_image_url)
            state = ChallengeState(answer=daily_answer,
                                   attempts=0,
                                   max_attempts=Config.DAILY_CHALLENGE_MAX_GUESSES,
                                   is_completed=False,
                                   past_guesses=())
            self._storage.save_state(user_id, state)
            logger.info(f"Created new session for {user_id}")

        return state

    def get_supported_emojis(self) -> tuple[EmojiData, ...]:
        return self._emoji_service.fetch_all_supported_emoji_metadata()

    def process_guess(self, user_id: str, codepoint_couple_guess: EmojiCodepointCouple) -> ChallengeState:
        state = self.get_user_state(user_id)

        if state.is_completed:
            return state

        is_correct_guess = codepoint_couple_guess == state.answer.emoji_codepoint_couple
        logger.info(f"User '{user_id}' made a guess with codepoints: {codepoint_couple_guess}. Attempts: {state.attempts}/{state.max_attempts}. Guess correct: {is_correct_guess}")
        emoji_couple_guess = EmojiDataCouple(first_emoji=self._emoji_service.fetch_emoji_by_codepoint(codepoint_couple_guess.first_emoji_codepoint),
                                             second_emoji=self._emoji_service.fetch_emoji_by_codepoint(codepoint_couple_guess.second_emoji_codepoint))
        new_state = ChallengeState(answer=state.answer,
                                   attempts=state.attempts + 1,
                                   max_attempts=state.max_attempts,
                                   is_completed=is_correct_guess,
                                   past_guesses=tuple([*state.past_guesses,
                                                       emoji_couple_guess]))
        self._storage.save_state(user_id, new_state)
        return new_state

    def _pick_daily_combination(self) -> CombinationData:
        emojis = self._emoji_service.fetch_all_supported_emoji_codepoints()
        random.seed(int(date.today().strftime("%Y%m%d")))

        for _ in range(self._max_combination_retries):
            first_codepoint = random.choice(emojis)
            available_combinations = self._emoji_service.fetch_available_codepoints_for_combination(first_codepoint)
            second_codepoint = random.choice(available_combinations)

            combination = self._emoji_service.fetch_combination_data(first_codepoint, second_codepoint)
            if combination is not None:
                logger.info(f"Daily emoji couple to guess : {combination.emoji_couple}")
                return combination
        raise ValueError(f"No combination could be found after {self._max_combination_retries} retries.")


if __name__ == '__main__':
    from src.utils.logger_coonfigurator import LoggerConfigurator
    from src.utils.path_handler import PathHandler
    from src.persistence.file_emoji_repository import FileEmojiRepository
    from src.persistence.file_challenge_storage import FileChallengeStorage

    LoggerConfigurator.config_logger()
    emoji_repository = FileEmojiRepository(PathHandler.src_dir / "emojis.json")
    challenge_repository = FileChallengeStorage(PathHandler.src_dir / "daily.json")
    with emoji_repository as repo:
        emoji_service = EmojiKitchenService(repo)
        game_service = DailyChallengeService(emoji_service, challenge_repository)

        user_id = "test_user"
        state = game_service.get_user_state(user_id)
        print(state)
        couple_guess = EmojiCodepointCouple("u1f600", "u1f600")
        guess_state = game_service.process_guess(user_id, couple_guess)
        print(guess_state)
