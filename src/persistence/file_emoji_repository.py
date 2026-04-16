import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.core.dto.combination_data import CombinationData
from src.core.dto.emoji_data import EmojiData
from src.persistence.abstract_emoji_repository import AbstractEmojiRepository

logger = logging.getLogger(__name__)


class FileEmojiRepository(AbstractEmojiRepository):
    def __init__(self, storage_path: Path):
        self._storage_path = storage_path
        self._cache: Dict[str, Any] = {}

    def __enter__(self) -> "FileEmojiRepository":
        if self._storage_path.exists():
            self._load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._save()

    def get_all_raw_emojis(self) -> Dict[str, Any]:
        return self._cache

    def get_raw_emoji(self, codepoint: str) -> Optional[Dict[str, Any]]:
        return self._cache.get(codepoint)

    def save_raw_emoji(self, codepoint: str, data: Dict[str, Any]):
        if codepoint not in self._cache:
            self._cache[codepoint] = data

    def update_combination_entry(self, source_codepoint: str, target_codepoint: str, data: Dict[str, Any]):
        if source_codepoint in self._cache:
            self._cache[source_codepoint]["combinations"][target_codepoint] = data

    def _load(self):
        if self._storage_path.exists():
            with self._storage_path.open("r", encoding="utf-8") as f:
                self._cache = json.load(f)

    def _save(self):
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self._storage_path.open("w", encoding="utf-8") as f:
            json.dump(self._cache, f, indent=2, ensure_ascii=False)
