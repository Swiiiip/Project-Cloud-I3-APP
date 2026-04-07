from abc import ABC, abstractmethod
from typing import Any, List, Optional

from src.persistence.abstract_database_connection import AbstractDatabaseConnection


class AbstractRepository(ABC):
    def __init__(self, db_connection: AbstractDatabaseConnection):
        self.db = db_connection

    @abstractmethod
    def save(self, entity: Any) -> None:
        pass

    @abstractmethod
    def find_by_id(self, entity_id: Any) -> Optional[Any]:
        pass

    @abstractmethod
    def find_all(self) -> List[Any]:
        pass

    @abstractmethod
    def delete(self, entity_id: Any) -> None:
        pass
