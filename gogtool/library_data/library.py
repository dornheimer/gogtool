from datetime import datetime
import json
import os

from gogtool.helper.directory import Directory
from gogtool.library_data.game import GameData
from gogtool.helper.log import logger


class LibraryData(Directory):
    """
    Library data imported from lgogdownloader's gamedetails.json.
    """
    def __init__(self, path):
        super().__init__(path)
        self.library_data = {}

        self.date = None
        self.games = {}

        self._get_library_data()
        self._initialize_library()

    def _get_library_data(self):
        """Convert gamedetails.json file into a python dictionary."""
        with open(self.path) as data:
            library_data = json.load(data)

        self.library_data = library_data
        logger.debug(f"imported data from {os.path.basename(self.path)}")

    def _initialize_library(self):
        self.date = self.library_data["date"]

        for game_data in self.library_data["games"]:
            self.games[game_data["gamename"]] = GameData(game_data)

    @property
    def games_list(self):
        return list(self.games)

    @property
    def game_titles(self):
        return [g.title for g in self.games.values()]

    @property
    def size(self):
        return len(self.games)

    @property
    def is_outdated(self):
        """Check if game details file is older than two days."""
        logger.info("Checking games data creation date...")
        creation_date = datetime.strptime(self.date, "%Y%m%dT%H%M%S")
        days_since_last_update = (datetime.now() - creation_date).days
        outdated = days_since_last_update >= 2

        str_outdated = "needs update" if outdated else "ok"
        logger.debug("gamedetails.json created on: {}, age: {} days ({})".format(
                     creation_date.strftime('%Y%m%d'), days_since_last_update, str_outdated))

        return outdated

    def get_game_data(self, game_name):
        """Get data associated with game from the library data.

        :param game_name: Game name as stored in DownloadDir.
        :return: Dictionary entry for game_name.
        """
        try:
            return self.games[game_name]
        except KeyError:
            logger.warning(f"Game info for {game_name} not found")
            return None
