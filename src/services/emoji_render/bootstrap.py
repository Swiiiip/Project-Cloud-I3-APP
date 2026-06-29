from src.config.constants import GameRules, Http, Network, ServicePorts
from src.config.loader import load_game_engine_service_base_url
from src.services.emoji_render.app import create_app
from src.services.emoji_render.game_engine_service_client import GameEngineServiceClient


class EmojiRenderBootstrap:
    @staticmethod
    def create_application():
        game_engine_client = GameEngineServiceClient(
            game_engine_service_base_url=load_game_engine_service_base_url(),
            timeout_seconds=Http.INTERNAL_TIMEOUT_SECONDS,
        )
        return create_app(
            game_engine_client,
            blur_levels=GameRules.DAILY_CHALLENGE_MAX_GUESSES,
        )

    @staticmethod
    def bind_host() -> str:
        return Network.BIND_HOST

    @staticmethod
    def bind_port() -> int:
        return ServicePorts.EMOJI_RENDER
