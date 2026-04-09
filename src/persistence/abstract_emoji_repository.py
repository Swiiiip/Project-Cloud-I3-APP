from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class AbstractEmojiRepository(ABC):
    @abstractmethod
    def __enter__(self) -> "AbstractEmojiRepository":
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def get_all_raw_emojis(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_raw_emoji(self, codepoint: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_raw_emoji(self, codepoint: str, data: Dict[str, Any]):
        pass

    @abstractmethod
    def update_combination_entry(self, source_codepoint: str, target_codepoint: str, data: Dict[str, Any]):
        pass
