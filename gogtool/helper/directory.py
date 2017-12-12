import os
import sys

from gogtool.helper.log import logger


class Directory:
    """
    Base class that verifies if an object is instantiated with a valid path.
    """
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
                logger.error(f"{type(self).__name__} could not be initialized: '{path}' does not exist.")
                sys.exit(2)
        self._path = path
        logger.debug(f"{type(self).__name__} initialized with {self.path}")
