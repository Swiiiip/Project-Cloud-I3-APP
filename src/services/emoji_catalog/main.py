import uvicorn
from dotenv import load_dotenv

from src.services.emoji_catalog.app import create_app
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler
from src.utils.runtime_env import RuntimeEnv


def main() -> None:
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)
    app = create_app()
    uvicorn.run(
        app,
        host=RuntimeEnv.require_str("CATALOG_SERVICE_HOST"),
        port=RuntimeEnv.require_int("CATALOG_SERVICE_PORT"),
    )


if __name__ == "__main__":
    main()
