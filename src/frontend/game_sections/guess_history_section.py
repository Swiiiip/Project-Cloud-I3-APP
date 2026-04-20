import logging
from typing import Awaitable, Callable

from nicegui import run, ui

from src.core.emoji.dto.emoji_couple import EmojiDataCouple
from src.core.gameplay.dto.challenge_state import ChallengeState
from src.frontend.ui_constants import UIClasses, UIColors, UIContent, UIIcons, UIProps, format_attempts_label, format_guess_pair
from src.frontend.view_model import BlurmojiViewModel

logger = logging.getLogger(__name__)


class GuessHistorySection:
    def __init__(self, view_model: BlurmojiViewModel, on_guess_submitted: Callable[[], Awaitable[None]]):
        self._view_model = view_model
        self._on_guess_submitted = on_guess_submitted

    @ui.refreshable
    def render(self):
        state = self._view_model.state
        if not state:
            logger.info('GuessHistorySection waiting for challenge state')
            with ui.card().classes(UIClasses.PANEL_CARD_CENTERED):
                ui.spinner(size='lg')
            return

        with ui.column().classes(UIClasses.WORKBENCH_CONTAINER):
            self._render_workbench()
            self._render_history(state)

    def _render_workbench(self):
        with ui.card().classes(UIClasses.WORKBENCH_CARD):
            with ui.row().classes(UIClasses.WORKBENCH_ROW):
                with ui.row().classes(UIClasses.SLOT_ROW):
                    ui.label().bind_text_from(self._view_model, 'char_1').classes(UIClasses.SLOT_LABEL)
                    ui.label().bind_text_from(self._view_model, 'char_2').classes(UIClasses.SLOT_LABEL)
                with ui.row().classes(UIClasses.SLOT_ROW):
                    submit_button = ui.button(icon=UIIcons.SUBMIT, on_click=self._submit_guess).props(UIProps.ROUND_BUTTON)
                    submit_button.bind_enabled_from(self._view_model, 'can_submit')
                    submit_button.bind_background_color_from(
                        self._view_model,
                        'can_submit',
                        lambda can_submit: UIColors.SUBMIT_ENABLED if can_submit else UIColors.SUBMIT_DISABLED,
                    )
                    ui.button(icon=UIIcons.RESET, on_click=self._reset_selection).props(UIProps.DELETE_BUTTON)

        logger.info('Rendered workbench with current selections %s and %s', self._view_model.char_1, self._view_model.char_2)

    @staticmethod
    def _render_history(state: ChallengeState):
        attempts_history = state.past_guesses
        with ui.card().classes(UIClasses.HISTORY_CARD):
            with ui.column().classes(UIClasses.HISTORY_SCROLL):
                ui.label(format_attempts_label(state.attempts, state.max_attempts)).classes(UIClasses.ATTEMPTS_META)
                for index in range(state.max_attempts):
                    with ui.row().classes(UIClasses.ATTEMPT_ROW):
                        if index < len(attempts_history):
                            guessed_emoji_couple: EmojiDataCouple = attempts_history[index]
                            ui.label(
                                format_guess_pair(
                                    guessed_emoji_couple.first_emoji.character,
                                    guessed_emoji_couple.second_emoji.character,
                                )
                            ).classes(UIClasses.ATTEMPT_GUESS)
                            ui.icon(UIIcons.FAILED_ATTEMPT, color=UIColors.ERROR_ICON).classes(UIClasses.ATTEMPT_ICON)
                        else:
                            ui.label(UIContent.EMPTY_ATTEMPT_LABEL).classes(UIClasses.ATTEMPT_EMPTY)

        logger.info('Rendered history with %d entries', len(attempts_history))

    async def _submit_guess(self):
        logger.info('Submitting guess from GuessHistorySection')
        state = await run.io_bound(self._view_model.submit_guess)
        if state is None:
            logger.info('Guess submission ignored because state is unavailable')
            return
        await self.render.refresh()
        await self._on_guess_submitted()

    def _reset_selection(self):
        self._view_model.reset_selection()
        logger.info('Selection reset from GuessHistorySection')
