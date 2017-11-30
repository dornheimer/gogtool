"""Application wide logger."""
import logging
import logging.handlers
import os

levels = {"debug": logging.DEBUG,
          "info": logging.INFO,
          "warning": logging.WARNING,
          "error": logging.ERROR,
          "critical": logging.CRITICAL}

LOG_FILENAME = os.path.join(os.getenv("HOME"), "python/lgog_manager/lgog.log")
log_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                   maxBytes=1048576,
                                                   backupCount=1)

log_format = "[%(levelname)s:%(name)s:%(funcName)s]: %(message)s"
log_formatter = logging.Formatter(log_format)
log_handler.setFormatter(log_formatter)

console = logging.StreamHandler()
console_format = "%(asctime)s %(levelname)s:[%(module)s:%(funcName)s]: %(message)s"
date_fmt = "%H:%M:%S"
console_formatter = logging.Formatter(console_format, date_fmt)
console.setFormatter(console_formatter)

logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
logger.addHandler(console)
logger.setLevel(logging.WARNING)

logger.debug(f"logger '{logger.name}' created")
