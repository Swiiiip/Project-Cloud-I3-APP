from abc import ABC, abstractmethod
from typing import Tuple

from src.core.dto.emoji_combination import EmojiCombination
from src.core.dto.emoji_data import EmojiData


class AbstractEmojiRepository(ABC):
    @abstractmethod
    def __enter__(self) -> "AbstractEmojiRepository":
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def fetch_supported_emojis(self) -> Tuple[EmojiData]:
        pass

    @abstractmethod
    def fetch_emoji_combinations(self,
                                 reference_emoji: EmojiData) -> Tuple[EmojiCombination]:
        pass

    @abstractmethod
    def add_emoji_combination(self,
                              emoji_combination: EmojiCombination):
        pass

    @abstractmethod
    def add_supported_emoji(self,
                            emoji_data: EmojiData):
        pass
