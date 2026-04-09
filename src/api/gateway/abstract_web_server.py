from abc import ABC, abstractmethod
from typing import Callable


class AbstractWebServer(ABC):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    @abstractmethod
    def add_route(self, path: str, handler: Callable, method: str) -> None:
        pass

    @abstractmethod
    def start(self, debug: bool) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
