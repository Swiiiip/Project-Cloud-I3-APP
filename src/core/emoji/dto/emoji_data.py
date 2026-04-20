from dataclasses import dataclass

from typing import Any


@dataclass(frozen=True)
class EmojiData:
    name: str
    character: str
    codepoint: str
    keyboard_position: int  # TODO might be useless...
    keywords: list[str]
    category: str
    subcategory: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EmojiData":
        return cls(
            name=data["name"],
            character=data["character"],
            codepoint=data["codepoint"],
            keyboard_position=data["keyboardPosition"],
            keywords=data["keywords"],
            category=data["category"],
            subcategory=data["subcategory"]
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "character": self.character,
            "codepoint": self.codepoint,
            "keyboardPosition": self.keyboard_position,
            "keywords": self.keywords,
            "category": self.category,
            "subcategory": self.subcategory,
            "combinations": {}
        }
