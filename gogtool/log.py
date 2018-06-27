import logging
import logging.handlers

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


def configure_logger(log_level='debug', log_file=None):

    logger = logging.getLogger('gogtool')
    logger.setLevel(logging.DEBUG)

    if log_file is not None:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1048576, backupCount=1)

        file_format = "[%(levelname)-6s:%(name)s:%(funcName)s] %(message)s"
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)

    console = logging.StreamHandler()
    console_format = "%(levelname)-8s[%(module)s:%(funcName)s] %(message)s"
    date_fmt = "%H:%M:%S"
    console_formatter = logging.Formatter(console_format, date_fmt)
    console.setFormatter(console_formatter)
    console.setLevel(LOG_LEVELS[log_level])

    # Prevent adding duplicate handlers
    if not len(logger.handlers):
        if log_file is not None:
            logger.addHandler(file_handler)
        logger.addHandler(console)

    return logger
