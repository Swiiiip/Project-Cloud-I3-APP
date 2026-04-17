import time
from typing import Optional
from nicegui import ui

from src.core.emoji.dto.emoji_data import EmojiData
from src.frontend.game_client import GameClient


class BlurmojiView:
    def __init__(self, api_client: GameClient):
        self._client = api_client
        self._user_id = "daily_user_1"
        self._state = {}
        self._emoji_pool = self._client.get_supported_emojis()

        self._char_1 = '?'
        self._char_2 = '?'
        self._selection_1: Optional[EmojiData] = None
        self._selection_2: Optional[EmojiData] = None
        self._can_confirm = False
        self._past_guesses = []

    def load_initial_data(self):
        try:
            self._state = self._client.create_daily_challenge(self._user_id)
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
        else:
            ui.notify("Slots full!", color='warning')

    def _reset_selection(self):
        self._selection_1 = None
        self._selection_2 = None
        self._char_1 = '?'
        self._char_2 = '?'
        self._can_confirm = False

    def _submit_guess(self):
        if not self._selection_1 or not self._selection_2:
            return
        try:
            # Update state with API response
            self._state = self._client.make_guess(
                self._user_id,
                self._selection_1.codepoint,
                self._selection_2.codepoint
            )
            self._past_guesses.append(f"{self._selection_1.character} {self._selection_2.character}")
            self._reset_selection()

            # Force full UI refresh to show history and new image
            self.render.refresh()

            if not self._state.get("is_won") and not self._state.get("is_completed"):
                ui.notify("Wrong! Image clarifying...", type='info')
        except Exception as e:
            ui.notify(f"Error: {e}", type='negative')

    @ui.refreshable
    def render(self):
        if not self._state:
            ui.spinner(size='lg').classes('absolute-center')
            return

        # Explicitly pull data from state
        is_completed = self._state["is_completed"]
        attempts = self._state["attempts"]
        max_attempts = self._state["max_attempts"]

        # Use URL instead of PIL object for reliable NiceGUI image rendering
        # Cache bust with attempts and timestamp
        img_url = f"{self._client.get_rendered_image_url(self._user_id)}&t={time.time()}"

        with ui.column().classes('w-full items-center gap-6 p-4'):
            # 1. Image Card
            with ui.card().classes('p-4 bg-[#1e1e1e] border-2 border-[#333] shadow-xl'):
                ui.image(img_url).style('width: 260px; height: 260px; background: #000;')
                if is_completed:
                    win = self._state["is_won"]
                    ui.label("🏆 SOLVED" if win else "❌ FAILED").classes(
                        f'text-center font-bold text-xl mt-2 {"text-green-500" if win else "text-red-500"}'
                    )

            # 2. Selection Workbench
            with ui.row().classes('items-center gap-4 bg-[#262626] p-4 rounded-xl border border-[#444]'):
                with ui.row().classes('gap-2'):
                    ui.label().bind_text_from(self, '_char_1').classes(
                        'w-14 h-14 flex items-center justify-center bg-[#1a1a1a] rounded-lg text-3xl border-2 border-[#555]'
                    )
                    ui.label().bind_text_from(self, '_char_2').classes(
                        'w-14 h-14 flex items-center justify-center bg-[#1a1a1a] rounded-lg text-3xl border-2 border-[#555]'
                    )

                with ui.column().classes('gap-1'):
                    ui.button(icon='check', on_click=self._submit_guess).props('round color=green') \
                        .bind_visibility_from(self, '_can_confirm')
                    ui.button(icon='delete', on_click=self._reset_selection).props('round flat color=grey')

            # 3. History
            self._render_stats(attempts, max_attempts)

            # 4. Keyboard
            self._render_keyboard(is_completed)

    def _render_stats(self, attempts: int, max_attempts: int):
        with ui.column().classes('w-full max-w-sm gap-2'):
            ui.label(f'ATTEMPTS: {attempts} / {max_attempts}').classes(
                'text-gray-400 text-xs font-black tracking-widest')
            for i in range(max_attempts):
                with ui.row().classes(
                        'w-full justify-between items-center bg-[#1e1e1e] p-2 rounded-lg border border-[#222] h-14'):
                    if i < len(self._past_guesses):
                        # Show the pair from history
                        ui.label(self._past_guesses[i]).classes('text-2xl ml-2')
                        ui.icon('close', color='red-500').classes('mr-2')
                    else:
                        ui.label('• •').classes('text-gray-800 text-2xl ml-2')

    def _render_keyboard(self, is_completed: bool):
        with ui.card().classes('bg-[#1e1e1e] p-4 w-full max-w-2xl border border-[#333] shadow-inner'):
            with ui.row().classes('justify-center gap-2'):
                for emoji in self._emoji_pool:
                    ui.button(emoji.character, on_click=lambda e=emoji: self._handle_selection(e)) \
                        .props('flat') \
                        .classes('text-3xl p-1 rounded-lg hover:bg-white/10') \
                        .bind_enabled_from(self._state, 'is_completed', backward=lambda x: not x)
