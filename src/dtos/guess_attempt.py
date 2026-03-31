from dataclasses import dataclass
from datetime import datetime


@dataclass
class GuessAttempt:
    emojis: list[str]
    timestamp: datetime
    is_correct: bool
