from collections.abc import Mapping
import os
import sys

from gogtool.helper.log import logger


class Directory(Mapping):
    """
    Base class that verifies if an object is instantiated with a valid path.
    """
    def __init__(self, path):
        self.path = path
        self._games = {}

    def __len__(self):
        return len(self._games)

    def __getitem__(self, game_name):
        if game_name not in self._games:
            try:
                raise KeyError
            except KeyError:
                logger.debug(f"Could not find '{game_name}' in {type(self).__name__}")
                return None
        return self._games[game_name]

    def __iter__(self):
        return iter(self._games)

    def __repr__(self):
        return f"{type(self).__name__!r}({self.path!r})"

    def __str__(self):
        return type(self).__name__

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

    @property
    def games(self):
        return list(self._games)
