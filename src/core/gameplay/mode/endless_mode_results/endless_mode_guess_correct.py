from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class EndlessModeGuessCorrect:
    correct: bool
    score: int
    streak: int
    next_emoji: Optional[str]

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
