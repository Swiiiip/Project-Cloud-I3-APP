import json
import os
from typing import Any, Dict, Optional

from src.persistence.abstract_database_connection import AbstractDatabaseConnection


class FileDatabaseConnection(AbstractDatabaseConnection):
    def __init__(self, base_path: str = ".game_state"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def execute(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if query.startswith("SAVE"):
            table, data = query.split(" ", 2)[1], params
            self._save_to_file(table, data)
        elif query.startswith("LOAD"):
            table = query.split(" ", 1)[1]
            return self._load_from_file(table)
        elif query.startswith("DELETE"):
            table = query.split(" ", 1)[1]
            self._delete_file(table)
        return None

    def _save_to_file(self, filename: str, data: Dict[str, Any]) -> None:
        path = os.path.join(self.base_path, f"{filename}.json")
        with open(path, "w") as f:
            json.dump(data, f)

    def _load_from_file(self, filename: str) -> Optional[Dict[str, Any]]:
        path = os.path.join(self.base_path, f"{filename}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return None

    def _delete_file(self, filename: str) -> None:
        path = os.path.join(self.base_path, f"{filename}.json")
        if os.path.exists(path):
            os.remove(path)
