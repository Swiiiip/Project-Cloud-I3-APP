from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class EndlessModeStateSnapshot:
    game_id: str
    score: int
    attempts: int
    is_completed: bool
    streak: int
    max_streak: int
    current_emoji: Optional[str]

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
