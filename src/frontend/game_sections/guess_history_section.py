import logging
from typing import Awaitable, Callable

from nicegui import run, ui

from src.core.emoji.dto.emoji_couple import EmojiDataCouple
from src.core.gameplay.dto.challenge_state import ChallengeState
from src.frontend.ui_constants import UIClasses, UIColors, UIContent, UIIcons, UIProps, format_guess_pair
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
            self._render_workbench(state)
            self._render_history(state)
            self._render_communication_block(state)

    def _render_workbench(self, state: ChallengeState):
        is_game_over = state.is_completed or (state.attempts >= state.max_attempts and not state.is_completed)
        with ui.card().classes(UIClasses.WORKBENCH_CARD):
            with ui.row().classes(UIClasses.WORKBENCH_ROW):
                with ui.row().classes(UIClasses.SLOT_ROW):
                    ui.label().bind_text_from(self._view_model, 'char_1').classes(UIClasses.SLOT_LABEL)
                    ui.label().bind_text_from(self._view_model, 'char_2').classes(UIClasses.SLOT_LABEL)
                with ui.row().classes(UIClasses.SLOT_ROW):
                    submit_button = ui.button(icon=UIIcons.SUBMIT, on_click=self._submit_guess).props(UIProps.ROUND_BUTTON)
                    submit_button.bind_enabled_from(self._view_model, 'can_submit')
                    submit_button.enabled = submit_button.enabled and not is_game_over
                    submit_button.bind_background_color_from(
                        self._view_model,
                        'can_submit',
                        lambda can_submit: UIColors.SUBMIT_ENABLED if can_submit and not is_game_over else UIColors.SUBMIT_DISABLED,
                    )
                    ui.button(icon=UIIcons.RESET, on_click=self._reset_selection).props(UIProps.DELETE_BUTTON)

        logger.info('Rendered workbench with current selections %s and %s', self._view_model.char_1, self._view_model.char_2)

    def _render_history(self, state: ChallengeState):
        attempts_history = state.past_guesses
        with ui.card().classes(UIClasses.HISTORY_CARD):
            with ui.column().classes(UIClasses.HISTORY_SCROLL):
                for index in range(state.max_attempts):
                    with ui.row().classes(UIClasses.ATTEMPT_ROW):
                        if index < len(attempts_history):
                            guessed_emoji_couple: EmojiDataCouple = attempts_history[index]
                            first_class, second_class = self._emoji_slot_classes(state, guessed_emoji_couple)
                            with ui.row().classes(UIClasses.ATTEMPT_PAIR):
                                ui.label(guessed_emoji_couple.first_emoji.character).classes(first_class)
                                ui.label(guessed_emoji_couple.second_emoji.character).classes(second_class)
                        else:
                            with ui.row().classes(UIClasses.ATTEMPT_PAIR):
                                ui.label("").classes(UIClasses.ATTEMPT_EMPTY)
                                ui.label("").classes(UIClasses.ATTEMPT_EMPTY)

        logger.info('Rendered history with %d entries', len(attempts_history))

    def _render_communication_block(self, state: ChallengeState):
        with ui.card().classes(UIClasses.COMMUNICATION_CARD):
            if self._is_success(state):
                ui.label(UIContent.SUCCESS_MESSAGE).classes(UIClasses.COMMUNICATION_SUCCESS)
                ui.label(UIContent.CHALLENGE_NAME_TEMPLATE.format(name=state.answer.name)).classes(UIClasses.COMMUNICATION_TEXT)
                return

            if self._is_failure(state):
                first_emoji, second_emoji = self._resolve_answer_characters(state)
                ui.label(format_guess_pair(first_emoji, second_emoji)).classes(UIClasses.COMMUNICATION_TEXT)
                ui.label(UIContent.FAILURE_MESSAGE).classes(UIClasses.COMMUNICATION_FAILURE)
                ui.label(UIContent.CHALLENGE_NAME_TEMPLATE.format(name=state.answer.name)).classes(UIClasses.COMMUNICATION_TEXT)
                return

            ui.label(' ').classes(UIClasses.COMMUNICATION_PLACEHOLDER)

    @staticmethod
    def _is_success(state: ChallengeState) -> bool:
        return state.is_completed

    @staticmethod
    def _is_failure(state: ChallengeState) -> bool:
        return state.attempts >= state.max_attempts and not state.is_completed

    @staticmethod
    def _emoji_slot_classes(state: ChallengeState, guessed_emoji_couple: EmojiDataCouple) -> tuple[str, str]:
        answer = state.answer.emoji_codepoint_couple
        answer_remaining: dict[str, int] = {}
        for answer_codepoint in (answer.first_emoji_codepoint, answer.second_emoji_codepoint):
            answer_remaining[answer_codepoint] = answer_remaining.get(answer_codepoint, 0) + 1

        slot_classes: list[str] = []
        for guessed_codepoint in (
            guessed_emoji_couple.first_emoji.codepoint,
            guessed_emoji_couple.second_emoji.codepoint,
        ):
            available = answer_remaining.get(guessed_codepoint, 0)
            if available > 0:
                slot_classes.append(UIClasses.ATTEMPT_GUESS_CORRECT)
                answer_remaining[guessed_codepoint] = available - 1
            else:
                slot_classes.append(UIClasses.ATTEMPT_GUESS_INCORRECT)

        return slot_classes[0], slot_classes[1]

    def _resolve_answer_characters(self, state: ChallengeState) -> tuple[str, str]:
        answer = state.answer.emoji_codepoint_couple
        return (
            self._resolve_emoji_character(answer.first_emoji_codepoint),
            self._resolve_emoji_character(answer.second_emoji_codepoint),
        )

    def _resolve_emoji_character(self, target_codepoint: str) -> str:
        for category in self._view_model.emoji_pool:
            for emoji in category.emojis:
                if emoji.codepoint == target_codepoint:
                    return emoji.character

        normalized_codepoint = target_codepoint.lower().removeprefix('u')
        try:
            return ''.join(chr(int(part, 16)) for part in normalized_codepoint.split('-'))
        except ValueError:
            logger.warning('Could not resolve emoji character for codepoint=%s', target_codepoint)
            return target_codepoint

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
