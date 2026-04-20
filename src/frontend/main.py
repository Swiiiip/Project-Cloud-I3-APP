import os

from dotenv import load_dotenv
from nicegui import ui
from nicegui.events import KeyEventArguments
from src.frontend.game_sections import ChallengeImageSection, EmojiGridSection, GuessHistorySection
from src.frontend.game_view import BlurmojiView
from src.frontend.session_state import FrontendSessionState
from src.frontend.state.abstract_frontend_state_provider import AbstractFrontendStateProvider
from src.frontend.state.in_memory_frontend_state_provider import InMemoryFrontendStateProvider
from src.frontend.ui_constants import UIClasses, UIColors, UIContent
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler


class WebHandler:
    def __init__(self,
                 host: str,
                 port: int,
                 state_provider: AbstractFrontendStateProvider):
        self._host = host
        self._port = port
        self._state_provider = state_provider

    def _get_session_state(self) -> FrontendSessionState:
        return self._state_provider.get_state()

    def run(self, reload: bool):
        @ui.page('/')
        def main_page():
            ui.colors(primary=UIColors.SUBMIT_ENABLED, secondary=UIColors.SUBMIT_DISABLED)
            ui.query('body').classes(UIClasses.BODY)

            session_state = self._get_session_state()
            image_section = ChallengeImageSection(session_state.view_model)
            guess_history_section = GuessHistorySection(
                session_state.view_model,
                on_guess_submitted=image_section.render.refresh
            )
            emoji_grid_section = EmojiGridSection(session_state.view_model, guess_history_section)
            view = BlurmojiView(session_state.view_model, image_section, guess_history_section, emoji_grid_section)

            def handle_backspace_shortcut(event: KeyEventArguments) -> None:
                if not event.action.keydown or not event.key.backspace:
                    return
                if session_state.view_model.remove_last_selection():
                    guess_history_section.render.refresh()

            ui.keyboard(on_key=handle_backspace_shortcut, repeating=False)

            with ui.header().classes(UIClasses.HEADER):
                ui.label(UIContent.APP_TITLE).classes(UIClasses.HEADER_TITLE)

            view.render()
            ui.timer(0.1, view.load_initial_data, once=True)

        ui.run(
            title=UIContent.APP_TITLE,
            dark=True,
            host=self._host,
            port=self._port,
            reload=reload
        )


if __name__ == '__main__':
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)

    web = WebHandler(host=os.environ["FRONTEND_HOST"],
                     port=int(os.environ["FRONTEND_PORT"]),
                     state_provider=InMemoryFrontendStateProvider(os.environ["API_BASE_URL"]))
    web.run(reload=False)
