import threading

from src.frontend.game_client import GameClient
from src.frontend.state.session_state import FrontendSessionState
from src.frontend.state.abstract_frontend_state_provider import AbstractFrontendStateProvider
from src.frontend.view.view_model import BlurmojiViewModel
from src.utils.runtime_env import RuntimeEnv


class InMemoryFrontendStateProvider(AbstractFrontendStateProvider):
    def __init__(self, api_base_url: str):
        self._api_base_url = api_base_url
        self._state: FrontendSessionState | None = None
        self._lock = threading.Lock()

    def get_state(self) -> FrontendSessionState:
        with self._lock:
            if self._state is None:
                client = GameClient(base_url=self._api_base_url, request_timeout_seconds=RuntimeEnv.require_int("INTERNAL_HTTP_TIMEOUT_SECONDS"))
                view_model = BlurmojiViewModel(client)
                self._state = FrontendSessionState(client=client, view_model=view_model)
            state = self._state
        return state
