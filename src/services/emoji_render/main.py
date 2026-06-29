import uvicorn

from src.services.emoji_render.bootstrap import EmojiRenderBootstrap
from src.utils.logger_configurator import LoggerConfigurator


def main() -> None:
    LoggerConfigurator.config_logger()
    app = EmojiRenderBootstrap.create_application()
    uvicorn.run(app, host=EmojiRenderBootstrap.bind_host(), port=EmojiRenderBootstrap.bind_port())


if __name__ == "__main__":
    main()
