from typing import Callable

from flask import Flask

from src.api.gateway.abstract_web_server import AbstractWebServer


class FlaskWebServer(AbstractWebServer):
    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.app = Flask(__name__)

    def add_route(self, path: str, handler: Callable, method: str) -> None:
        self.app.add_url_rule(path, view_func=handler, methods=[method])

    def start(self, debug: bool) -> None:
        self.app.run(host=self.host, port=self.port, debug=debug)

    def stop(self) -> None:
        pass
