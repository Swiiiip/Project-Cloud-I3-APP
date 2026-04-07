from abc import ABC, abstractmethod
from typing import Callable


class AbstractWebServer(ABC):
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port

    @abstractmethod
    def add_route(self, path: str, handler: Callable, method: str = "GET") -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
