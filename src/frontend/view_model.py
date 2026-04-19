import asyncio
import logging
from typing import Optional

from PIL.Image import Image

from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple
from src.core.emoji.dto.emoji_data import EmojiData
from src.core.gameplay.dto.challenge_state import ChallengeState
from src.frontend.game_client import GameClient

logger = logging.getLogger(__name__)


class BlurmojiViewModel:
    _default_unselected_char = '?'

    def __init__(self, client: GameClient):
        self._client = client
        self._initial_data_lock = asyncio.Lock()
        self._state: Optional[ChallengeState] = None
        self._emoji_pool: tuple[EmojiData, ...] = ()
        self._rendered_image: Optional[Image] = None
        self._char_1 = self._default_unselected_char
        self._char_2 = self._default_unselected_char
        self._selection_1: Optional[EmojiData] = None
        self._selection_2: Optional[EmojiData] = None
        self._can_confirm = False

    @property
    def state(self) -> Optional[ChallengeState]:
        return self._state

    @property
    def emoji_pool(self) -> tuple[EmojiData, ...]:
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
            logger.info("Loading initial game data")
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
        if not self._state or self._state.is_completed:
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

    def submit_guess(self) -> Optional[ChallengeState]:
        if not self._state or not (self._selection_1 and self._selection_2):
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
