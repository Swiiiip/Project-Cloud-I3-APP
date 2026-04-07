import sys
from logging import getLogger, INFO
import logging

logger = getLogger(__name__)


class LoggerConfigurator:
    @classmethod
    def config_logger(cls):
        logger.setLevel(INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
