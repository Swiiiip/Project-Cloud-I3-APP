import os

from dotenv import load_dotenv

from src.api.gateway.flask_web_server import FlaskWebServer
from src.api.routes.game_routes import GameRoutes
from src.core.service.emoji_kitchen.emoji_service import EmojiKitchenService
from src.persistence.abstract_emoji_repository import AbstractEmojiRepository
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler


class GameApi:
    def __init__(self,
                 host: str,
                 port: int,
                 emoji_repository: AbstractEmojiRepository,
                 use_cache: bool = True):
        self.web_server = FlaskWebServer(host=host,
                                         port=port)
        self._emoji_kitchen_service = EmojiKitchenService(repository=emoji_repository)
        self.routes = GameRoutes()
        self._setup_routes()
        if not use_cache:
            self._emoji_kitchen_service.populate_repository()

    def run(self, debug: bool = False):
        self.web_server.start(debug=debug)

    def _setup_routes(self):
        self.web_server.add_route("/api/daily-challenge", self.routes.create_daily_challenge, "POST")
        self.web_server.add_route("/api/endless", self.routes.create_endless_game, "POST")
        self.web_server.add_route("/api/guess", self.routes.make_guess, "POST")
        self.web_server.add_route("/api/game/<game_id>", self.routes.get_game_status, "GET")
        self.web_server.add_route("/api/end-game", self.routes.end_game, "POST")


if __name__ == "__main__":
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)
    api = GameApi(host=os.environ["API_HOST"],
                  port=int(os.environ["API_PORT"]))
    api.run()
