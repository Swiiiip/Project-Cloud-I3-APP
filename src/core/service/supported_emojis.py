from dataclasses import asdict, dataclass

from typing import Dict, Any, List


@dataclass(frozen=True)
class SupportedEmojis:
    emojis: List[str]

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
