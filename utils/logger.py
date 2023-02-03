from utils.loader import config
import logging
from logging import handlers


def init_logger(name, logger_level="DEBUG", file_level="INFO", console_level="DEBUG"):
    """
    "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL"
    """

    # main configuration of logger
    logger = logging.getLogger(name)
    logger.setLevel(logger_level)
    log_message = '%(asctime)s ; %(name)s:%(lineno)s ; %(levelname)s ; %(message)s'

    # handling console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter(log_message))
    logger.addHandler(console_handler)

    # handling file logging
    file_handler = logging.handlers.RotatingFileHandler(filename=config.main_log, maxBytes=1000000,
                                                        backupCount=5)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(logging.Formatter(log_message))
    logger.addHandler(file_handler)

    return logger
