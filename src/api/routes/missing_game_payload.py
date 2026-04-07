from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class MissingGamePayload:
    error: str

    def to_json_dict(self) -> Dict[str, Any]:
        return {"error": self.error}
