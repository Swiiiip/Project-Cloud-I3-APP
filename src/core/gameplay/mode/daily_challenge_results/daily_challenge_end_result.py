from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class DailyChallengeEndResult:
    status: str
    final_score: int
    total_attempts: int

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
