from src.core.gameplay.mode.daily_challenge_results.daily_challenge_end_result import DailyChallengeEndResult
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_guess_completed import DailyChallengeGuessCompleted
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_guess_correct_progress import DailyChallengeGuessCorrectProgress
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_guess_result import DailyChallengeGuessResult
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_guess_wrong import DailyChallengeGuessWrong
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_start_result import DailyChallengeStartResult
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_status_result import DailyChallengeStatusResult
from src.core.gameplay.state.daily_challenge_state import DailyChallengeState


class DailyChallengeMode:
    def __init__(self, game_state: DailyChallengeState, supported_emojis: list[str]):
        self.game_state = game_state
        self.supported_emojis = supported_emojis

    def start_game(self) -> DailyChallengeStartResult:
        self.game_state.daily_emojis = self.supported_emojis
        return DailyChallengeStartResult(
            status="started",
            game_id=self.game_state.game_id,
            emojis_to_guess=len(self.supported_emojis),
        )

    def make_guess(self, guess: str) -> DailyChallengeGuessResult:
        self.game_state.increment_attempts()

        if guess in self.supported_emojis and guess not in self.game_state.guessed_emojis:
            self.game_state.add_guessed_emoji(guess)
            self.game_state.update_score(10)

            if len(self.game_state.guessed_emojis) == len(self.supported_emojis):
                self.game_state.complete_game()
                return DailyChallengeGuessCompleted(
                    correct=True,
                    completed=True,
                    score=self.game_state.score,
                    message="Daily challenge completed!",
                )

            return DailyChallengeGuessCorrectProgress(
                correct=True,
                completed=False,
                score=self.game_state.score,
                remaining=len(self.supported_emojis) - len(self.game_state.guessed_emojis),
            )

        return DailyChallengeGuessWrong(
            correct=False,
            score=self.game_state.score,
            attempts=self.game_state.attempts,
        )

    def get_game_status(self) -> DailyChallengeStatusResult:
        return DailyChallengeStatusResult(
            game_id=self.game_state.game_id,
            score=self.game_state.score,
            attempts=self.game_state.attempts,
            completed=self.game_state.is_completed,
            guessed=list(self.game_state.guessed_emojis),
            remaining=len(self.supported_emojis) - len(self.game_state.guessed_emojis),
        )

    def end_game(self) -> DailyChallengeEndResult:
        self.game_state.complete_game()
        return DailyChallengeEndResult(
            status="ended",
            final_score=self.game_state.score,
            total_attempts=self.game_state.attempts,
        )
