from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class DailyChallengeStartResult:
    status: str
    game_id: str
    emojis_to_guess: int

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
