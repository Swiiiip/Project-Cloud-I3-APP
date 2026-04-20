import threading

from src.frontend.game_client import GameClient
from src.frontend.session_state import FrontendSessionState
from src.frontend.state.abstract_frontend_state_provider import AbstractFrontendStateProvider
from src.frontend.view_model import BlurmojiViewModel


class InMemoryFrontendStateProvider(AbstractFrontendStateProvider):
    def __init__(self, api_base_url: str):
        self._api_base_url = api_base_url
        self._state: FrontendSessionState | None = None
        self._lock = threading.Lock()

    def get_state(self) -> FrontendSessionState:
        with self._lock:
            if self._state is None:
                client = GameClient(base_url=self._api_base_url)
                view_model = BlurmojiViewModel(client)
                self._state = FrontendSessionState(client=client, view_model=view_model)
            state = self._state
        return state
