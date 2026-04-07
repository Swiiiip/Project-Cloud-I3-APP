from typing import Union

from src.core.gameplay.mode.daily_challenge_results.daily_challenge_guess_completed import DailyChallengeGuessCompleted
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_guess_correct_progress import DailyChallengeGuessCorrectProgress
from src.core.gameplay.mode.daily_challenge_results.daily_challenge_guess_wrong import DailyChallengeGuessWrong

DailyChallengeGuessResult = Union[
    DailyChallengeGuessCorrectProgress,
    DailyChallengeGuessCompleted,
    DailyChallengeGuessWrong,
]
