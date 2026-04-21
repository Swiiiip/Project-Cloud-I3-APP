from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    passed: bool
    details: str

