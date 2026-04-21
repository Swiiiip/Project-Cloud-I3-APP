import json
import threading
from pathlib import Path
from typing import Optional

from src.core.gameplay.dto.challenge_state import ChallengeState
from src.persistence.challenge_storage.abstract_challenge_storage import AbstractChallengeStorage


class FileChallengeStorage(AbstractChallengeStorage):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        if not self.file_path.exists():
            self.file_path.write_text("{}", encoding="utf-8")
        self._lock = threading.Lock()
        self._data_cache = self._load_all()

    def _load_all(self) -> dict[str, str]:
        with open(self.file_path, 'r', encoding="utf-8") as f:
            return json.load(f)

    def _save_all(self, data: dict[str, str]):
        with open(self.file_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def save_state(self, session_id: str, state: ChallengeState) -> None:
        with self._lock:
            self._data_cache[session_id] = state.model_dump_json()
            self._save_all(self._data_cache)

    def get_state(self, session_id: str) -> Optional[ChallengeState]:
        with self._lock:
            state_json = self._data_cache.get(session_id)
        if not state_json:
            return None
        return ChallengeState.model_validate_json(state_json)

    def delete_state(self, session_id: str) -> None:
        with self._lock:
            if session_id in self._data_cache:
                del self._data_cache[session_id]
                self._save_all(self._data_cache)
