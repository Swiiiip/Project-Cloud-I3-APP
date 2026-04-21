from abc import ABC, abstractmethod


class AbstractGuessSubmitter(ABC):
    @abstractmethod
    async def submit_guess(self) -> None:
        pass

