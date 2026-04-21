import json
import logging
import threading
from pathlib import Path
from typing import Any, Optional

from src.persistence.emoji_repository.abstract_emoji_repository import AbstractEmojiRepository

logger = logging.getLogger(__name__)


class FileEmojiRepository(AbstractEmojiRepository):
    def __init__(self, storage_path: Path):
        self._storage_path = storage_path
        self._cache: dict[str, Any] = {}
        self._loaded = False
        self._is_dirty = False
        self._lock = threading.Lock()

    def __enter__(self) -> "FileEmojiRepository":
        with self._lock:
            if not self._loaded:
                self._load()
                self._loaded = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._lock:
            if exc_type is None and self._is_dirty:
                self._save()
                self._is_dirty = False

    def get_all_raw_emojis(self) -> dict[str, Any]:
        return self._cache

    def get_raw_emoji(self, codepoint: str) -> Optional[dict[str, Any]]:
        return self._cache.get(codepoint)

    def save_raw_emoji(self, codepoint: str, data: dict[str, Any]):
        if codepoint not in self._cache:
            self._cache[codepoint] = data
            self._is_dirty = True

    def update_combination_entry(self, source_codepoint: str, target_codepoint: str, data: dict[str, Any]):
        if source_codepoint in self._cache:
            combinations = self._cache[source_codepoint].setdefault("combinations", {})
            if combinations.get(target_codepoint) != data:
                combinations[target_codepoint] = data
                self._is_dirty = True

    def _load(self):
        if self._storage_path.exists():
            with self._storage_path.open("r", encoding="utf-8") as f:
                self._cache = json.load(f)
        else:
            self._cache = {}

    def _save(self):
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self._storage_path.open("w", encoding="utf-8") as f:
            json.dump(self._cache, f, indent=2, ensure_ascii=False)
