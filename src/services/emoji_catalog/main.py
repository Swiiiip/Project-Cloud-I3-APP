import uvicorn

from src.services.emoji_catalog.bootstrap import EmojiCatalogBootstrap
from src.utils.logger_configurator import LoggerConfigurator


def main() -> None:
    LoggerConfigurator.config_logger()
    app = EmojiCatalogBootstrap.create_application()
    uvicorn.run(app, host=EmojiCatalogBootstrap.bind_host(), port=EmojiCatalogBootstrap.bind_port())


if __name__ == "__main__":
    main()
