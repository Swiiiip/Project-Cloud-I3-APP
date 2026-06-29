from src.config.constants import Network, ServicePorts
from src.services.emoji_catalog.app import create_app


class EmojiCatalogBootstrap:
    @staticmethod
    def create_application():
        return create_app()

    @staticmethod
    def bind_host() -> str:
        return Network.BIND_HOST

    @staticmethod
    def bind_port() -> int:
        return ServicePorts.EMOJI_CATALOG
