import logging
from typing import Awaitable, Callable

from nicegui import run, ui

from src.core.emoji.dto.emoji_couple import EmojiDataCouple
from src.core.gameplay.dto.challenge_state import ChallengeState
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
            with ui.card().classes('w-full h-full bg-[#1e1e1e] border border-[#333] items-center justify-center'):
                ui.spinner(size='lg')
            return

        with ui.column().classes('w-full h-full gap-3 overflow-hidden'):
            self._render_workbench()
            self._render_history(state)

    def _render_workbench(self):
        with ui.card().classes('w-full bg-[#1e1e1e] border border-[#333] p-3'):
            with ui.row().classes('items-center justify-between gap-3'):
                with ui.row().classes('gap-2'):
                    ui.label().bind_text_from(self._view_model, '_char_1').classes('w-14 h-14 flex items-center justify-center bg-[#111] rounded-lg text-3xl border border-[#555]')
                    ui.label().bind_text_from(self._view_model, '_char_2').classes('w-14 h-14 flex items-center justify-center bg-[#111] rounded-lg text-3xl border border-[#555]')
                with ui.row().classes('gap-2'):
                    ui.button(icon='check', on_click=self._submit_guess).props('round color=green').bind_visibility_from(self._view_model, '_can_confirm')
                    ui.button(icon='delete', on_click=self._reset_selection).props('round flat color=grey')

        logger.info('Rendered workbench with current selections %s and %s', self._view_model.char_1, self._view_model.char_2)

    @staticmethod
    def _render_history(state: ChallengeState):
        attempts_history = state.past_guesses
        with ui.card().classes('w-full flex-1 bg-[#1e1e1e] border border-[#333] p-3 overflow-hidden'):
            with ui.column().classes('w-full h-full gap-2 overflow-auto pr-1'):
                ui.label(f'ATTEMPTS: {state.attempts} / {state.max_attempts}').classes('text-gray-400 text-xs font-black')
                for index in range(state.max_attempts):
                    with ui.row().classes('w-full justify-between items-center bg-[#151515] p-2 rounded-lg border border-[#222] h-12'):
                        if index < len(attempts_history):
                            guessed_emoji_couple: EmojiDataCouple = attempts_history[index]
                            ui.label(f'{guessed_emoji_couple.first_emoji.character} • {guessed_emoji_couple.second_emoji.character}').classes('text-2xl ml-2')
                            ui.icon('close', color='red-500').classes('mr-2')
                        else:
                            ui.label('• •').classes('text-gray-800 text-2xl ml-2')

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
