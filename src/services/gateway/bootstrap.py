from src.config.constants import Http, Network, ServicePorts
from src.config.loader import load_service_urls, load_session_cookie_secret
from src.services.gateway.app import create_app
from src.services.gateway.internal_client import InternalServiceClient
from src.services.gateway.signed_cookie_session_resolver import SignedCookieSessionResolver


class GatewayBootstrap:
    @staticmethod
    def create_application():
        service_urls = load_service_urls()
        internal_client = InternalServiceClient(
            game_engine_service_base_url=service_urls.game_engine,
            emoji_catalog_service_base_url=service_urls.emoji_catalog,
            emoji_render_service_base_url=service_urls.emoji_render,
            timeout_seconds=Http.INTERNAL_TIMEOUT_SECONDS,
        )
        session_resolver = SignedCookieSessionResolver(load_session_cookie_secret())
        return create_app(internal_client, session_resolver)

    @staticmethod
    def bind_host() -> str:
        return Network.BIND_HOST

    @staticmethod
    def bind_port() -> int:
        return ServicePorts.GATEWAY
