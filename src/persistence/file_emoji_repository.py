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


if __name__ == '__main__':
    repo = FileEmojiRepository(Path("test_cache.json"))
    reference_emoji = EmojiData(
        name="coffee",
        character="☕",
        codepoint="2615",
        keyboard_position=1,
        keywords=["coffee", "hot beverage"],
        category="Food & Drink",
        subcategory="hot beverage"
    )
    combo_emoji = EmojiData(
        name="red_heart",
        character="❤️",
        codepoint="2665-fe0f",
        keyboard_position=1,
        keywords=["heart", "love"],
        category="Symbols",
        subcategory="heart"
    )

    combination_data = CombinationData(
        first_emoji=reference_emoji,
        second_emoji=combo_emoji,
        result_image_url="www.example.com",
        name="coffee-heart")

    with repo as r:
        r.add_supported_emoji(reference_emoji)
        r.add_emoji_combination(combination_data)
