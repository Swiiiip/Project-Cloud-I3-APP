from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class DailyChallengeGuessWrong:
    correct: bool
    score: int
    attempts: int

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
