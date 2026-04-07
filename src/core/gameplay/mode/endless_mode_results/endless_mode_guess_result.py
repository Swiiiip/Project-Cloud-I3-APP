from typing import Union

from src.core.gameplay.mode.endless_mode_results.endless_mode_guess_correct import EndlessModeGuessCorrect
from src.core.gameplay.mode.endless_mode_results.endless_mode_guess_wrong import EndlessModeGuessWrong

EndlessModeGuessResult = Union[EndlessModeGuessCorrect, EndlessModeGuessWrong]
