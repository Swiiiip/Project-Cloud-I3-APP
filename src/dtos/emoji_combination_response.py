from dataclasses import dataclass, asdict


@dataclass
class EmojiCombinationResponse:
    image_url: str
    alt: str
    date: str

    def to_dict(self) -> dict:
        return asdict(self)
