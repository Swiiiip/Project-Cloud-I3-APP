from src.config.constants import Http, Network, ServicePorts
from src.config.loader import load_api_base_url
from src.frontend.state.in_memory_frontend_state_provider import InMemoryFrontendStateProvider


class FrontendBootstrap:
    @staticmethod
    def create_state_provider() -> InMemoryFrontendStateProvider:
        return InMemoryFrontendStateProvider(
            api_base_url=load_api_base_url(),
            request_timeout_seconds=Http.INTERNAL_TIMEOUT_SECONDS,
        )

    @staticmethod
    def bind_host() -> str:
        return Network.BIND_HOST

    @staticmethod
    def bind_port() -> int:
        return ServicePorts.FRONTEND
