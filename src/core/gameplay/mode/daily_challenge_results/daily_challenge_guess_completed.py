from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class DailyChallengeGuessCompleted:
    correct: bool
    completed: bool
    score: int
    message: str

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
