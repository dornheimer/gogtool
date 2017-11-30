import os
import sys

from lgog.helper.log import logger


class Directory:
    def __init__(self, path):
        self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if not os.path.exists(path):
            try:
                raise FileNotFoundError("Path to directory does not exist.")
            except:
                logger.error(f"Directory '{path}' does not exist.")
                sys.exit(2)
        self._path = path
        logger.debug(f"{type(self).__name__} initialized with {self.path}")
