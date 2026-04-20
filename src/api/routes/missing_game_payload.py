from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MissingGamePayload:
    error: str

    def to_json_dict(self) -> dict[str, Any]:
        return {"error": self.error}
