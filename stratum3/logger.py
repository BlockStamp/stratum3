import logging

from stratum3 import settings


def get_logger(name):
    logger = logging.getLogger(name)
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)
    logger.setLevel(getattr(logging, settings.LOGLEVEL))
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s # %(message)s")
    )
    return logger
