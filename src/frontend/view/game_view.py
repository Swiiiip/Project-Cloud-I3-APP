import logging

from nicegui import ui

from src.frontend.view.game_sections import ChallengeImageSection, EmojiGridSection, GuessHistorySection
from src.frontend.view.ui_constants import UIClasses
from src.frontend.view.view_model import BlurmojiViewModel

logger = logging.getLogger(__name__)


class BlurmojiView:
    def __init__(self, view_model: BlurmojiViewModel, image_section: ChallengeImageSection,
                 guess_history_section: GuessHistorySection, emoji_grid_section: EmojiGridSection):
        self._view_model = view_model
        self._image_section = image_section
        self._guess_history_section = guess_history_section
        self._emoji_grid_section = emoji_grid_section

    async def load_initial_data(self):
        try:
            await self._view_model.load_initial_data()
            logger.info("Initial game data loaded")
            await self._image_section.render.refresh()
            await self._guess_history_section.render.refresh()
            await self._emoji_grid_section.render.refresh()
        except Exception as e:
            logger.exception("Failed to initialize frontend data: %s", e)

    async def on_guess_submitted(self):
        await self._image_section.render.refresh()
        await self._emoji_grid_section.render.refresh()

    def render(self):
        with ui.row().classes(UIClasses.MAIN_LAYOUT):
            with ui.column().classes(f'{UIClasses.COLUMN_BASE} {UIClasses.IMAGE_COLUMN}'):
                self._image_section.render()
            with ui.column().classes(f'{UIClasses.COLUMN_BASE} {UIClasses.HISTORY_COLUMN}'):
                self._guess_history_section.render()
            with ui.column().classes(f'{UIClasses.COLUMN_BASE} {UIClasses.EMOJI_COLUMN}'):
                self._emoji_grid_section.render()
