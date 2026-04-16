import os

import uvicorn
from dotenv import load_dotenv

from src.api.bootstrapper import BlurmojiApiBootstrapper
from src.utils.logger_coonfigurator import LoggerConfigurator
from src.utils.path_handler import PathHandler


def main():
    LoggerConfigurator.config_logger()
    load_dotenv(dotenv_path=PathHandler.dot_env(), override=False)

    server = BlurmojiApiBootstrapper()
    uvicorn.run(server.app,
                host=os.environ["API_HOST"],
                port=int(os.environ["API_PORT"]))


if __name__ == '__main__':
    main()
