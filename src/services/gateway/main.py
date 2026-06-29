import uvicorn

from src.services.gateway.bootstrap import GatewayBootstrap
from src.utils.logger_configurator import LoggerConfigurator


def main() -> None:
    LoggerConfigurator.config_logger()
    app = GatewayBootstrap.create_application()
    uvicorn.run(app, host=GatewayBootstrap.bind_host(), port=GatewayBootstrap.bind_port())


if __name__ == "__main__":
    main()
