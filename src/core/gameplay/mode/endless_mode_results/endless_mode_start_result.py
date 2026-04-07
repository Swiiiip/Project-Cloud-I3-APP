from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class EndlessModeStartResult:
    status: str
    game_id: str
    current_emoji: Optional[str]

    def to_json_dict(self) -> Dict[str, Any]:
        return asdict(self)
