"""Application wide logger."""

import logging
import logging.handlers
import os

levels = {"debug": logging.DEBUG,
          "info": logging.INFO,
          "warning": logging.WARNING,
          "error": logging.ERROR,
          "critical": logging.CRITICAL}

LOG_FILENAME = os.path.join(os.getenv("HOME"), "python/lgog_manager/gogtool.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                    maxBytes=1048576,
                                                    backupCount=1)

file_format = "[%(levelname)-6s:%(name)s:%(funcName)s]: %(message)s"
file_formatter = logging.Formatter(file_format)
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console_format = "%(asctime)s %(levelname)-8s[%(module)s:%(funcName)s]: %(message)s"
date_fmt = "%H:%M:%S"
console_formatter = logging.Formatter(console_format, date_fmt)
console.setFormatter(console_formatter)
console.setLevel(logging.WARNING)

logger.addHandler(file_handler)
logger.addHandler(console)

logger.debug(f"logger '{logger.name}' created")
