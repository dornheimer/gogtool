from datetime import datetime
import json
import os

from .game import GameData
from gogtool.helper.directory import Directory
from gogtool.helper.log import logger


class LibraryData(Directory):
    """
    Library data imported from lgogdownloader's gamedetails.json.
    """
    def __init__(self, path):
        super().__init__(path)
        self._library_data = {}

        self._import_library_data()
        self._initialize_library()

    def __iter__(self):
        return iter(self._games.values())

    def _import_library_data(self):
        """Convert gamedetails.json file into a python dictionary."""
        with open(self.path) as data:
            library_data = json.load(data)

        self._library_data = library_data
        logger.debug(f"imported data from {os.path.basename(self.path)}")

    def _initialize_library(self):
        for game_data in self._library_data["games"]:
            game_name = game_data["gamename"]
            self._games[game_name] = GameData(game_data)

    @property
    def game_titles(self):
        return [game.title for game in self]

    @property
    def is_outdated(self):
        """Check if game details file is older than two days."""
        logger.info("Checking games data creation date...")
        date = self._library_data["date"]
        creation_date = datetime.strptime(date, "%Y%m%dT%H%M%S")
        days_since_last_update = (datetime.now() - creation_date).days
        outdated = days_since_last_update >= 2

        str_outdated = "needs update" if outdated else "ok"
        logger.debug("gamedetails.json created on: {}, age: {} days ({})".format(
                     creation_date.strftime('%Y%m%d'), days_since_last_update, str_outdated))

        return outdated
