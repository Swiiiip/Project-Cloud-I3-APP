import os
from dotenv import load_dotenv

from src.api.gateway.flask_web_server import FlaskWebServer
from src.api.routes.game_routes import GameRoutes
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler


class GameApi:
    def __init__(self,
                 host: str,
                 port: int):
        self.web_server = FlaskWebServer(host=host,
                                         port=port)
        self.routes = GameRoutes()
        self._setup_routes()

    def _setup_routes(self):
        self.web_server.add_route("/api/supported-emojis", self.routes.get_supported_emojis, "GET")
        self.web_server.add_route("/api/daily-challenge", self.routes.create_daily_challenge, "POST")
        self.web_server.add_route("/api/endless", self.routes.create_endless_game, "POST")
        self.web_server.add_route("/api/guess", self.routes.make_guess, "POST")
        self.web_server.add_route("/api/game/<game_id>", self.routes.get_game_status, "GET")
        self.web_server.add_route("/api/end-game", self.routes.end_game, "POST")

    def run(self, debug: bool = False):
        self.web_server.start(debug=debug)


if __name__ == "__main__":
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)
    GameApi(host=os.environ["API_HOST"],
            port=int(os.environ["API_PORT"])).run()
