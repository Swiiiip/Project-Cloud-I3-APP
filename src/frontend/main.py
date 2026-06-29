from nicegui import ui
from nicegui.events import KeyEventArguments
from src.frontend.view.game_sections import ChallengeImageSection, EmojiGridSection, GuessHistorySection
from src.frontend.view.game_view import BlurmojiView
from src.frontend.state.session_state import FrontendSessionState
from src.frontend.state.abstract_frontend_state_provider import AbstractFrontendStateProvider
from src.frontend.view.ui_constants import UIClasses, UIColors, UIContent
from src.frontend.bootstrap import FrontendBootstrap
from src.utils.logger_configurator import LoggerConfigurator


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

    def close(self) -> None:
        close = getattr(self._state_provider, "close", None)
        if callable(close):
            close()


if __name__ == '__main__':
    LoggerConfigurator.config_logger()
    web = WebHandler(
        host=FrontendBootstrap.bind_host(),
        port=FrontendBootstrap.bind_port(),
        state_provider=FrontendBootstrap.create_state_provider(),
    )
    try:
        web.run(reload=False)
    finally:
        web.close()
