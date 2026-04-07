from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AbstractDatabaseConnection(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def execute(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        pass
