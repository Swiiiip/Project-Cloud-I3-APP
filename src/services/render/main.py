import uvicorn
from dotenv import load_dotenv

from src.services.render.app import create_app
from src.services.render.game_service_client import GameServiceClient
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler
from src.utils.runtime_env import RuntimeEnv


def main() -> None:
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)
    game_client = GameServiceClient(
        game_service_base_url=RuntimeEnv.require_str("GAME_SERVICE_BASE_URL"),
        timeout_seconds=RuntimeEnv.require_int("INTERNAL_HTTP_TIMEOUT_SECONDS"),
    )
    app = create_app(game_client)
    uvicorn.run(
        app,
        host=RuntimeEnv.require_str("RENDER_SERVICE_HOST"),
        port=RuntimeEnv.require_int("RENDER_SERVICE_PORT"),
    )


if __name__ == "__main__":
    main()
