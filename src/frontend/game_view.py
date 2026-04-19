from typing import Optional

from PIL.Image import Image
from nicegui import ui

from src.core.emoji.dto.emoji_couple import EmojiCodepointCouple, EmojiDataCouple
from src.core.emoji.dto.emoji_data import EmojiData
from src.core.gameplay.dto.challenge_state import ChallengeState
from src.frontend.game_client import GameClient


class BlurmojiView:
    _state: ChallengeState = None
    _default_unselected_char = '?'

    def __init__(self, api_client: GameClient):
        self._client = api_client
        self._emoji_pool = self._client.get_supported_emojis()

        self._char_1 = self._default_unselected_char
        self._char_2 = self._default_unselected_char
        self._selection_1: Optional[EmojiData] = None
        self._selection_2: Optional[EmojiData] = None
        self._can_confirm = False

    def load_initial_data(self):
        try:
            self._state = self._client.create_daily_challenge()
            self.render.refresh()
        except Exception as e:
            ui.notify(f"Connection Error: {e}", type='negative')

    def _handle_selection(self, emoji: EmojiData):
        if not self._selection_1:
            self._selection_1 = emoji
            self._char_1 = emoji.character
        elif not self._selection_2:
            self._selection_2 = emoji
            self._char_2 = emoji.character
            self._can_confirm = True

    def _reset_selection(self):
        self._selection_1 = None
        self._selection_2 = None
        self._char_1 = self._default_unselected_char
        self._char_2 = self._default_unselected_char
        self._can_confirm = False

    def _submit_guess(self):
        if not (self._selection_1 and self._selection_2):
            return
        try:
            guess = EmojiCodepointCouple(first_emoji_codepoint=self._selection_1.codepoint,
                                         second_emoji_codepoint=self._selection_2.codepoint)
            self._state = self._client.make_guess(guess)
            self._reset_selection()
            self.render.refresh()
            if not self._state.is_completed:
                ui.notify("Wrong! Image clarifying...", type='info')
        except Exception as e:
            ui.notify(f"Error: {e}", type='negative')

    @ui.refreshable
    def render(self):
        if not self._state:
            ui.spinner(size='lg').classes('absolute-center')
            return

        rendered_image_bytes = self._client.get_rendered_image()
        with ui.column().classes('w-full items-center gap-6 p-4'):
            self._render_image_card(rendered_image_bytes)
            self._render_workbench()
            self._render_history()
            self._render_emoji_grid()

    def _render_image_card(self, rendered_image: Image):
        with ui.card().classes('p-4 bg-[#1e1e1e] border-2 border-[#333] shadow-xl'):
            ui.image(rendered_image).style('background: #000; width: 534px; height: 534px')
            if self._state.is_completed:
                result_text = "🏆 SOLVED" if self._state.is_completed else "❌ FAILED"
                result_color = "text-green-500" if self._state.is_completed else "text-red-500"
                ui.label(result_text).classes(f'text-center font-bold text-xl mt-2 {result_color}')

    def _render_workbench(self):
        with ui.row().classes('items-center gap-4 bg-[#262626] p-4 rounded-xl border border-[#444]'):
            with ui.row().classes('gap-2'):
                ui.label().bind_text_from(self, '_char_1').classes('w-14 h-14 flex items-center justify-center bg-[#1a1a1a] rounded-lg text-3xl border-2 border-[#555]')
                ui.label().bind_text_from(self, '_char_2').classes('w-14 h-14 flex items-center justify-center bg-[#1a1a1a] rounded-lg text-3xl border-2 border-[#555]')
            with ui.column().classes('gap-1'):
                ui.button(icon='check', on_click=self._submit_guess).props('round color=green').bind_visibility_from(self, '_can_confirm')
                ui.button(icon='delete', on_click=self._reset_selection).props('round flat color=grey')

    def _render_history(self):
        attempts_history = self._state.past_guesses
        with ui.column().classes('w-full max-w-sm gap-2'):
            ui.label(f'ATTEMPTS: {self._state.attempts} / {self._state.max_attempts}').classes('text-gray-400 text-xs font-black')
            for i in range(self._state.max_attempts):
                with ui.row().classes('w-full justify-between items-center bg-[#1e1e1e] p-2 rounded-lg border border-[#222] h-14'):
                    if i < len(self._state.past_guesses):
                        guessed_emoji_couple: EmojiDataCouple = attempts_history[i]
                        ui.label(f"{guessed_emoji_couple.first_emoji.character} {guessed_emoji_couple.second_emoji.character}").classes('text-2xl ml-2')
                        ui.icon('close', color='red-500').classes('mr-2')
                    else:
                        ui.label('• •').classes('text-gray-800 text-2xl ml-2')

    def _render_emoji_grid(self):
        is_disabled = self._state.is_completed
        with ui.card().classes('bg-[#1e1e1e] p-4 w-full max-w-2xl border border-[#333] shadow-inner'):
            with ui.row().classes('justify-center gap-2'):
                for emoji in self._emoji_pool:
                    ui.button(emoji.character, on_click=lambda e=emoji: self._handle_selection(e)) \
                        .props('flat') \
                        .classes('text-3xl p-1 rounded-lg hover:bg-white/10') \
                        .set_enabled(not is_disabled)
