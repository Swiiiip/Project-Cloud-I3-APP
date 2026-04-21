import asyncio
import logging
import threading
from typing import Optional

from PIL.Image import Image

from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple
from src.core.emoji.dto.emoji_category_data import EmojiCategoryData
from src.core.emoji.dto.emoji_data import EmojiData
from src.core.gameplay.dto.challenge_state import ChallengeState
from src.frontend.game_client import GameClient
from src.frontend.view.ui_constants import UIContent

logger = logging.getLogger(__name__)


class BlurmojiViewModel:
    _default_unselected_char = UIContent.DEFAULT_SLOT_CHAR

    def __init__(self, client: GameClient):
        self._client = client
        self._initial_data_lock = asyncio.Lock()
        self._initial_data_task: Optional[asyncio.Task[None]] = None
        self._state: Optional[ChallengeState] = None
        self._emoji_pool: tuple[EmojiCategoryData, ...] = ()
        self._rendered_image: Optional[Image] = None
        self._char_1 = self._default_unselected_char
        self._char_2 = self._default_unselected_char
        self._selection_1: Optional[EmojiData] = None
        self._selection_2: Optional[EmojiData] = None
        self._can_confirm = False
        self._is_submitting_guess = False
        self._submit_guess_lock = threading.Lock()

    @property
    def state(self) -> Optional[ChallengeState]:
        return self._state

    @property
    def emoji_pool(self) -> tuple[EmojiCategoryData, ...]:
        return self._emoji_pool

    @property
    def rendered_image(self) -> Optional[Image]:
        return self._rendered_image

    @property
    def char_1(self) -> str:
        return self._char_1

    @property
    def char_2(self) -> str:
        return self._char_2

    @property
    def can_submit(self) -> bool:
        return self._can_confirm and not self._is_submitting_guess and not self.is_interaction_locked

    @property
    def is_submitting_guess(self) -> bool:
        return self._is_submitting_guess

    @property
    def is_interaction_locked(self) -> bool:
        if self._state is None:
            return False
        return self._state.is_completed or self._state.attempts >= self._state.max_attempts

    def has_initial_data(self) -> bool:
        return self._state is not None and self._rendered_image is not None and len(self._emoji_pool) > 0

    async def load_initial_data(self) -> None:
        async with self._initial_data_lock:
            logger.info(
                "load_initial_data entered: has_state=%s has_image=%s emoji_pool_size=%d",
                self._state is not None,
                self._rendered_image is not None,
                len(self._emoji_pool),
            )
            if self.has_initial_data():
                logger.info("Using cached initial game data")
                return

            if self._initial_data_task is None or self._initial_data_task.done():
                logger.info("Loading initial game data")
                self._initial_data_task = asyncio.create_task(self._load_initial_data_once())
            else:
                logger.info("Awaiting in-flight initial data load")
            load_task = self._initial_data_task

        await load_task

    async def _load_initial_data_once(self) -> None:
        self._emoji_pool = await asyncio.to_thread(self._client.get_supported_emojis)
        logger.info("Loaded supported emojis: count=%d", len(self._emoji_pool))
        self._state = await asyncio.to_thread(self._client.create_daily_challenge)
        logger.info(
            "Loaded challenge state: attempts=%s max_attempts=%s completed=%s",
            self._state.attempts,
            self._state.max_attempts,
            self._state.is_completed,
        )
        self._rendered_image = await asyncio.to_thread(self._client.get_rendered_image)
        logger.info("Loaded rendered image: available=%s", self._rendered_image is not None)
        self.reset_selection()

    def select_emoji(self, emoji: EmojiData) -> None:
        if not self._state or self.is_interaction_locked or self._is_submitting_guess:
            logger.info("Ignoring emoji selection because challenge is unavailable or completed")
            return
        if self._selection_1 is None:
            self._selection_1 = emoji
            self._char_1 = emoji.character
            logger.info("Selected first emoji: codepoint=%s", emoji.codepoint)
            return
        if self._selection_2 is None:
            self._selection_2 = emoji
            self._char_2 = emoji.character
            self._can_confirm = True
            logger.info("Selected second emoji: codepoint=%s confirm_enabled=%s", emoji.codepoint, self._can_confirm)

    def reset_selection(self) -> None:
        self._selection_1 = None
        self._selection_2 = None
        self._char_1 = self._default_unselected_char
        self._char_2 = self._default_unselected_char
        self._can_confirm = False

    def remove_last_selection(self) -> bool:
        if not self._state or self.is_interaction_locked or self._is_submitting_guess:
            return False

        if self._selection_2 is not None:
            self._selection_2 = None
            self._char_2 = self._default_unselected_char
            self._can_confirm = False
            return True

        if self._selection_1 is not None:
            self._selection_1 = None
            self._char_1 = self._default_unselected_char
            self._can_confirm = False
            return True

        return False

    def submit_guess(self) -> Optional[ChallengeState]:
        if not self._submit_guess_lock.acquire(blocking=False):
            logger.info("submit_guess ignored: a submission is already being processed")
            return self._state

        self._is_submitting_guess = True
        try:
            if not self._state or self.is_interaction_locked or not (self._selection_1 and self._selection_2):
                logger.info("submit_guess skipped: has_state=%s has_selection_pair=%s", self._state is not None, self._selection_1 is not None and self._selection_2 is not None)
                return self._state

            guess = EmojiCodepointCouple(
                first_emoji_codepoint=self._selection_1.codepoint,
                second_emoji_codepoint=self._selection_2.codepoint
            )
            logger.info(
                "Submitting guess with codepoints %s and %s",
                guess.first_emoji_codepoint,
                guess.second_emoji_codepoint,
            )
            self._state = self._client.make_guess(guess)
            self._rendered_image = self._client.get_rendered_image()
            logger.info(
                "Guess result received: attempts=%s max_attempts=%s completed=%s",
                self._state.attempts,
                self._state.max_attempts,
                self._state.is_completed,
            )
            self.reset_selection()
            return self._state
        finally:
            self._is_submitting_guess = False
            self._submit_guess_lock.release()
