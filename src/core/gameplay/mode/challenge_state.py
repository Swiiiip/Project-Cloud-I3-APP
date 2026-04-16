from dataclasses import dataclass

from src.core.gameplay.mode.challenge_answer import ChallengeAnswer


@dataclass(frozen=True)
class ChallengeState:
    answer: ChallengeAnswer
    attempts: int
    max_attempts: int
    is_completed: bool

    @property
    def current_resolution_level(self) -> int:
        return self.attempts + 1

    def solve(self) -> "ChallengeState":
        return ChallengeState(answer=self.answer, attempts=self.attempts, max_attempts=self.max_attempts, is_completed=True)

    def increment_attempt(self) -> "ChallengeState":
        return ChallengeState(answer=self.answer, attempts=self.attempts + 1, max_attempts=self.max_attempts, is_completed=self.is_completed)
