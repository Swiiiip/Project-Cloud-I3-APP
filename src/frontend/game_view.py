from nicegui import ui

from src.frontend.game_client import GameClient


class BlurmojiView:
    def __init__(self, api_client: GameClient):
        self.client = api_client
        self.game_id = "daily_user_1"
        self.state = {}
        self.emoji_pool = []

    def load_initial_data(self):
        self.client.create_daily_challenge(self.game_id)
        self.emoji_pool = self.client.get_supported_emojis()
        self._update_local_state()

    def handle_guess(self, emoji: str):
        self.client.make_guess(self.game_id, emoji)
        self._update_local_state()

    def _update_local_state(self):
        self.state = self.client.get_status(self.game_id)
        self.render.refresh()

    @ui.refreshable
    def render(self):
        guesses = self.state.get("guesses", [])
        status = self.state.get("status", "playing")
        is_over = status in ["won", "lost"]

        # Blur calculation (Step-down from 30px to 0px)
        blur = max(0, 30 - (len(guesses) * 6)) if not is_over else 0

        with ui.column().classes('w-full items-center gap-6'):
            # Image Container
            with ui.element('div').classes('p-6 bg-[#1e1e1e] rounded-2xl shadow-lg'):
                ui.image(self.client.get_image() self.state.get("target_image_url")).style(
                    f'filter: blur({blur}px); width: 240px; transition: all 0.6s ease;'
                )

            # Guess Slots
            with ui.row().classes('gap-3'):
                for i in range(5):
                    char = guesses[i] if i < len(guesses) else ""
                    border = "border-[#333]"
                    if is_over and i == len(guesses) - 1:
                        border = "border-green-500" if status == "won" else "border-red-500"
                    elif i < len(guesses):
                        border = "border-red-500"

                    ui.label(char).classes(
                        f'w-12 h-12 flex items-center justify-center rounded-xl bg-[#1e1e1e] text-2xl border-2 {border}')

            # Keyboard Grid
            with ui.element('div').classes(
                    'grid grid-cols-6 sm:grid-cols-10 gap-2 p-4 bg-[#1e1e1e] rounded-2xl w-full max-w-xl'):
                for emoji in self.emoji_pool:
                    disabled = is_over or emoji in guesses
                    ui.button(emoji, on_click=lambda e=emoji: self.handle_guess(e)) \
                        .props('flat' + (' disabled' if disabled else '')) \
                        .classes('text-2xl hover:bg-[#333] rounded-lg')

            if is_over:
                ui.button('Reset Daily', on_click=self.load_initial_data).classes('bg-green-600 text-white px-8')
