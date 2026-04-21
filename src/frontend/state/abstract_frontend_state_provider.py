from abc import ABC, abstractmethod

from src.frontend.state.session_state import FrontendSessionState


class AbstractFrontendStateProvider(ABC):
    @abstractmethod
    def get_state(self) -> FrontendSessionState:
        pass

