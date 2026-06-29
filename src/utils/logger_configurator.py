import sys
from logging import getLogger, INFO
import logging

logger = getLogger(__name__)


class LoggerConfigurator:
    @classmethod
    def config_logger(cls):
        logging.basicConfig(level=INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            handlers=[logging.StreamHandler(sys.stdout)])
