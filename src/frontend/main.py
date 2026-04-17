import os
from dotenv import load_dotenv
from nicegui import ui

from src.frontend.game_client import GameClient
from src.frontend.game_view import BlurmojiView
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler


class WebHandler:
    def __init__(self, client: GameClient, host: str, port: int):
        self._client = client
        self._host = host
        self._port = port
        # Do NOT call load_initial_data here!
        self._ui = BlurmojiView(self._client)

    def run(self, reload: bool):
        @ui.page('/')
        def main_page():
            # Apply global styles
            ui.query('body').style('background-color: #121212; color: white;')

            with ui.header().classes('bg-[#1e1e1e] border-b border-[#333] items-center justify-center w-full'):
                ui.label('🤫 BLURMOJI').classes('text-2xl font-black tracking-tighter p-4')

            # This timer triggers AFTER the page is loaded and loop is running
            ui.timer(0.1, self._ui.load_initial_data, once=True)

            # Initial placeholder render
            self._ui.render()

        ui.run(
            title="Blurmoji",
            dark=True,
            host=self._host,
            port=self._port,
            reload=reload,
            storage_secret="pick_a_random_string_here"
        )


if __name__ == '__main__':
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)

    # Ensure environment variables exist
    api_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    host = os.environ.get("FRONTEND_HOST", "0.0.0.0")
    port = int(os.environ.get("FRONTEND_PORT", 8080))

    game_client = GameClient(base_url=api_url)

    handler = WebHandler(client=game_client, host=host, port=port)
    handler.run(reload=False)


if __name__ == '__main__':
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)
    game_client = GameClient(base_url=os.environ["API_BASE_URL"])
    WebHandler(client=game_client,
               host=os.environ["FRONTEND_HOST"],
               port=int(os.environ["FRONTEND_PORT"])).run(reload=False)
