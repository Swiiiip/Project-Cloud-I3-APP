from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class DailyChallengeStatusResult:
    game_id: str
    score: int
    attempts: int
    completed: bool
    guessed: List[str]
    remaining: int

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
