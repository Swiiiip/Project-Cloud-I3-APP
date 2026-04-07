import os

from dotenv import load_dotenv
from nicegui import ui

from src.frontend.game_client import GameClient
from src.frontend.game_view import BlurmojiView
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler


class WebHandler:
    def __init__(self,
                 client: GameClient,
                 host: str,
                 port: int):
        self._ui = BlurmojiView(client)
        self._host = host
        self._port = port

    def run(self,
            reload: bool):
        @ui.page('/')
        def main_page():
            ui.query('body').style('background-color: #121212; color: white; font-family: "Roboto", sans-serif;')
            with ui.header().classes('bg-[#1e1e1e] border-b border-[#333] justify-center'):
                ui.label('🤫 Blurmoji').classes('text-2xl font-bold p-2')

            ui.timer(0.1, self._ui.load_initial_data, once=True)
            self._ui.render()

        ui.run(
            title="Blurmoji",
            dark=True,
            host=self._host,
            port=self._port,
            reload=reload
        )


if __name__ == '__main__':
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)
    game_client = GameClient(base_url=os.environ["API_BASE_URL"])
    WebHandler(client=game_client,
               host=os.environ["FRONTEND_HOST"],
               port=int(os.environ["FRONTEND_PORT"])).run(reload=False)
