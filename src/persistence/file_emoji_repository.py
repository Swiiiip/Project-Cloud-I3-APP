import json
from pathlib import Path
from typing import Tuple, IO

from src.core.dto.emoji_combination import EmojiCombination
from src.core.dto.emoji_data import EmojiData
from src.persistence.abstract_emoji_repository import AbstractEmojiRepository


class FileEmojiRepository(AbstractEmojiRepository):
    _cache_file: IO

    def __init__(self, cache_path: Path):
        self._cache_path = cache_path
        self._content = {}
        if not self._cache_path.exists():
            self._cache_path.write_text(json.dumps({}))

    def __enter__(self):
        self._cache_file = self._cache_path.open("r+")
        self._content = json.load(self._cache_file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cache_file.seek(0)
        self._cache_file.truncate()
        json.dump(self._content, self._cache_file, sort_keys=True, indent=2)
        self._cache_file.close()

    def fetch_supported_emojis(self) -> Tuple[EmojiData, ...]:
        return tuple(EmojiData(name=data["name"],
                               codepoint=codepoint)
                     for codepoint, data in self._content.items())

    def fetch_emoji_combinations(self, reference_emoji: EmojiData) -> Tuple[EmojiCombination]:
        raw_combinations = self._content[reference_emoji.codepoint]["combinations"]
        return tuple([EmojiCombination.from_json_dict(combination) for combination in raw_combinations])

    def add_supported_emoji(self, emoji_data: EmojiData):
        self._content[emoji_data.codepoint] = {"name": emoji_data.name,
                                               "combinations": []}

    def add_emoji_combination(self, emoji_combination: EmojiCombination):
        if emoji_combination.first_emoji.codepoint not in self._content:
            self.add_supported_emoji(emoji_combination.first_emoji)

        existing_combinations = self.fetch_emoji_combinations(emoji_combination.first_emoji)

        is_duplicate = any(
            comb.first_emoji.codepoint == emoji_combination.first_emoji.codepoint and
            comb.second_emoji.codepoint == emoji_combination.second_emoji.codepoint
            for comb in existing_combinations
        )

        if not is_duplicate:
            self._content[emoji_combination.first_emoji.codepoint]["combinations"].append(
                emoji_combination.to_json_dict()
            )


if __name__ == '__main__':
    repo = FileEmojiRepository(Path("test_cache.json"))
    with repo as r:
        r.add_supported_emoji(EmojiData(name="😀", codepoint="1f600"))
        print(r.fetch_supported_emojis())
        r.add_emoji_combination(EmojiCombination(first_emoji=EmojiData(name="😀", codepoint="1f600"),
                                                 second_emoji=EmojiData(name="😀", codepoint="1f600"),
                                                 result_emoji=EmojiData(name="😀", codepoint="1f600"),
                                                 result_image_bytes="test"))
        print(r.fetch_emoji_combinations(EmojiData(name="😀", codepoint="1f600")))
        r.add_emoji_combination(EmojiCombination(first_emoji=EmojiData(name="😀", codepoint="1f600"),
                                                 second_emoji=EmojiData(name="😀", codepoint="1f600"),
                                                 result_emoji=EmojiData(name="😀", codepoint="1f600"),
                                                 result_image_bytes="test2"))
        print(r.fetch_emoji_combinations(EmojiData(name="😀", codepoint="1f600")))
