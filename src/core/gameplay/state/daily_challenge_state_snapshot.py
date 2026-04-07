from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Dict, List


@dataclass(frozen=True)
class DailyChallengeStateSnapshot:
    game_id: str
    score: int
    attempts: int
    is_completed: bool
    date: date
    daily_emojis: List[str]
    guessed_emojis: List[str]

    def to_json_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["date"] = self.date.isoformat()
        return d
