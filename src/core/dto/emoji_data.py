from dataclasses import asdict, dataclass

from typing import Dict, Any


@dataclass(frozen=True)
class EmojiData:
    name: str
    codepoint: str

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_json_dict(data: Dict[str, Any]):
        return EmojiData(**data)
