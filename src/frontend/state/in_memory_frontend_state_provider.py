import threading

from src.frontend.game_client import GameClient
from src.frontend.state.session_state import FrontendSessionState
from src.frontend.state.abstract_frontend_state_provider import AbstractFrontendStateProvider
from src.frontend.view.view_model import BlurmojiViewModel


class InMemoryFrontendStateProvider(AbstractFrontendStateProvider):
    def __init__(self, api_base_url: str, request_timeout_seconds: int):
        self._api_base_url = api_base_url
        self._request_timeout_seconds = request_timeout_seconds
        self._state: FrontendSessionState | None = None
        self._lock = threading.Lock()
        self._client: GameClient | None = None

    def close(self) -> None:
        with self._lock:
            if self._client is not None:
                self._client.close()
                self._client = None

    def get_state(self) -> FrontendSessionState:
        with self._lock:
            if self._state is None:
                self._client = GameClient(
                    base_url=self._api_base_url,
                    request_timeout_seconds=self._request_timeout_seconds,
                )
                view_model = BlurmojiViewModel(self._client)
                self._state = FrontendSessionState(view_model=view_model)
            state = self._state
        return state
