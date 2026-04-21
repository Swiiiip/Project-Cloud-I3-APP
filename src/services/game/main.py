import uvicorn
from dotenv import load_dotenv

from src.utils.runtime_env import RuntimeEnv
from src.services.game.app import create_app
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler


def main() -> None:
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)
    app = create_app()
    uvicorn.run(
        app,
        host=RuntimeEnv.require_str("GAME_SERVICE_HOST"),
        port=RuntimeEnv.require_int("GAME_SERVICE_PORT"),
    )


if __name__ == "__main__":
    main()

