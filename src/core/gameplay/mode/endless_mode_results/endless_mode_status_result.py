from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class EndlessModeStatusResult:
    game_id: str
    score: int
    attempts: int
    streak: int
    max_streak: int
    current_emoji: Optional[str]

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
