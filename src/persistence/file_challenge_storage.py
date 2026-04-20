import json
from pathlib import Path
from typing import Optional

from src.core.gameplay.dto.challenge_state import ChallengeState
from src.persistence.abstract_challenge_storage import AbstractChallengeStorage


class FileChallengeStorage(AbstractChallengeStorage):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        if not self.file_path.exists():
            self.file_path.write_text("{}")

    def _load_all(self) -> dict[str, str]:
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def _save_all(self, data: dict[str, str]):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def save_state(self, session_id: str, state: ChallengeState) -> None:
        data = self._load_all()
        data[session_id] = state.model_dump_json()
        self._save_all(data)

    def get_state(self, session_id: str) -> Optional[ChallengeState]:
        data = self._load_all()
        state_json = data.get(session_id)
        if not state_json:
            return None
        return ChallengeState.model_validate_json(state_json)

    def delete_state(self, session_id: str) -> None:
        data = self._load_all()
        if session_id in data:
            del data[session_id]
            self._save_all(data)
