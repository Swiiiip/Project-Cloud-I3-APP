import uvicorn

from src.services.game_engine.bootstrap import GameEngineBootstrap
from src.utils.logger_configurator import LoggerConfigurator


def main() -> None:
    LoggerConfigurator.config_logger()
    app = GameEngineBootstrap.create_application()
    uvicorn.run(app, host=GameEngineBootstrap.bind_host(), port=GameEngineBootstrap.bind_port())


if __name__ == "__main__":
    main()
