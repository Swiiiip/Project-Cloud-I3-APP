import logging
import random
import threading
from datetime import date

from src.core.emoji.dto.combination_data import CombinationData
from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple, EmojiDataCouple
from src.core.gameplay.dto.challenge_answer import ChallengeAnswer
from src.core.gameplay.dto.challenge_state import ChallengeState
from src.core.gameplay.dto.guess_slot_match import GuessSlotMatch
from src.core.emoji.emoji_kitchen import EmojiKitchenService
from src.persistence.challenge_storage.abstract_challenge_storage import AbstractChallengeStorage
from src.utils.runtime_env import RuntimeEnv

logger = logging.Logger(__name__)


class DailyChallengeService:
    _max_combination_retries = 3

    def __init__(self, emoji_service: EmojiKitchenService, storage: AbstractChallengeStorage):
        self._emoji_service = emoji_service
        self._storage = storage
        self._guess_locks: dict[str, threading.Lock] = {}
        self._guess_locks_guard = threading.Lock()
        self._daily_combination_lock = threading.Lock()
        self._cached_daily_combination_date: date | None = None
        self._cached_daily_combination: CombinationData | None = None

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
                                   max_attempts=RuntimeEnv.require_int("DAILY_CHALLENGE_MAX_GUESSES"),
                                   is_completed=False,
                                   past_guesses=(),
                                   past_guess_matches=())
            self._storage.save_state(user_id, state)
            logger.info(f"Created new session for {user_id}")

        if len(state.past_guess_matches) != len(state.past_guesses):
            state = self._with_backfilled_guess_matches(state)
            self._storage.save_state(user_id, state)
            logger.info("Backfilled guess match metadata for %s", user_id)

        return state

    def process_guess(self, user_id: str, codepoint_couple_guess: EmojiCodepointCouple) -> ChallengeState:
        guess_lock = self._get_guess_lock(user_id)
        if not guess_lock.acquire(blocking=False):
            logger.info("Ignoring concurrent guess for user '%s' while another submission is processing", user_id)
            return self.get_user_state(user_id)

        try:
            state = self.get_user_state(user_id)

            if state.is_completed:
                logger.info("Ignoring guess for user '%s' because user already won", user_id)
                return state

            is_correct_guess = self._is_correct_guess(codepoint_couple_guess, state.answer.emoji_codepoint_couple)
            logger.info(f"User '{user_id}' made a guess with codepoints: {codepoint_couple_guess}. Attempts: {state.attempts}/{state.max_attempts}. Guess correct: {is_correct_guess}")
            emoji_couple_guess = EmojiDataCouple(first_emoji=self._emoji_service.fetch_emoji_by_codepoint(codepoint_couple_guess.first_emoji_codepoint),
                                                 second_emoji=self._emoji_service.fetch_emoji_by_codepoint(codepoint_couple_guess.second_emoji_codepoint))
            guess_match = self._build_guess_slot_match(state.answer.emoji_codepoint_couple, codepoint_couple_guess)
            new_state = ChallengeState(answer=state.answer,
                                       attempts=state.attempts + 1,
                                       max_attempts=state.max_attempts,
                                       is_completed=is_correct_guess,
                                       past_guesses=tuple([*state.past_guesses,
                                                           emoji_couple_guess]),
                                       past_guess_matches=tuple([*state.past_guess_matches,
                                                                guess_match]))
            self._storage.save_state(user_id, new_state)
            return new_state
        finally:
            guess_lock.release()

    def _get_guess_lock(self, user_id: str) -> threading.Lock:
        with self._guess_locks_guard:
            guess_lock = self._guess_locks.get(user_id)
            if guess_lock is None:
                guess_lock = threading.Lock()
                self._guess_locks[user_id] = guess_lock
            return guess_lock

    @staticmethod
    def _build_guess_slot_match(answer: EmojiCodepointCouple, guess: EmojiCodepointCouple) -> GuessSlotMatch:
        answer_remaining: dict[str, int] = {}
        for answer_codepoint in (answer.first_emoji_codepoint, answer.second_emoji_codepoint):
            answer_remaining[answer_codepoint] = answer_remaining.get(answer_codepoint, 0) + 1

        slot_matches: list[bool] = []
        for guess_codepoint in (guess.first_emoji_codepoint, guess.second_emoji_codepoint):
            available = answer_remaining.get(guess_codepoint, 0)
            is_match = available > 0
            slot_matches.append(is_match)
            if is_match:
                answer_remaining[guess_codepoint] = available - 1

        return GuessSlotMatch(first_slot_match=slot_matches[0], second_slot_match=slot_matches[1])

    @staticmethod
    def _is_correct_guess(guess: EmojiCodepointCouple, answer: EmojiCodepointCouple) -> bool:
        return sorted((guess.first_emoji_codepoint, guess.second_emoji_codepoint)) == sorted(
            (answer.first_emoji_codepoint, answer.second_emoji_codepoint)
        )

    def _with_backfilled_guess_matches(self, state: ChallengeState) -> ChallengeState:
        computed_matches = tuple(
            self._build_guess_slot_match(
                state.answer.emoji_codepoint_couple,
                EmojiCodepointCouple(
                    first_emoji_codepoint=guess.first_emoji.codepoint,
                    second_emoji_codepoint=guess.second_emoji.codepoint,
                ),
            )
            for guess in state.past_guesses
        )
        return ChallengeState(
            answer=state.answer,
            attempts=state.attempts,
            max_attempts=state.max_attempts,
            is_completed=state.is_completed,
            past_guesses=state.past_guesses,
            past_guess_matches=computed_matches,
        )

    def _pick_daily_combination(self) -> CombinationData:
        today = date.today()
        with self._daily_combination_lock:
            if self._cached_daily_combination_date == today and self._cached_daily_combination is not None:
                return self._cached_daily_combination

        emojis = self._emoji_service.fetch_all_supported_emoji_codepoints()
        random.seed(int(today.strftime("%Y%m%d")))

        for _ in range(self._max_combination_retries):
            first_codepoint = random.choice(emojis)
            available_combinations = self._emoji_service.fetch_available_codepoints_for_combination(first_codepoint)
            second_codepoint = random.choice(available_combinations)

            combination = self._emoji_service.fetch_combination_data(first_codepoint, second_codepoint)
            if combination is not None:
                logger.info(f"Daily emoji couple to guess : {combination.emoji_couple}")
                with self._daily_combination_lock:
                    self._cached_daily_combination_date = today
                    self._cached_daily_combination = combination
                return combination
        raise ValueError(f"No combination could be found after {self._max_combination_retries} retries.")
