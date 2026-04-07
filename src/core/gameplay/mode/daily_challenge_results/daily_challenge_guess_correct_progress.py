from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class DailyChallengeGuessCorrectProgress:
    correct: bool
    completed: bool
    score: int
    remaining: int

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
