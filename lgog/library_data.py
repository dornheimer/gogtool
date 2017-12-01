from datetime import datetime
import json

from lgog.helper.directory import Directory
from lgog.helper.log import logger


class LibraryData(Directory):
    """
    User-specific GOG library data.
    """
    def __init__(self, path):
        super().__init__(path)
        self.library_data = self._get_library_data()
        self.games_list = self.library_data["games"]

    def _get_library_data(self):
        """Convert gamedetails.json file into a python dictionary."""
        with open(self.path) as data:
            library_data = json.load(data)

        return library_data

    @property
    def games(self):
        return [g["gamename"] for g in self.games_list]

    @property
    def size(self):
        return len(self.games_list)

    @property
    def is_outdated(self):
        """Check if game details file is older than two days."""
        logger.info("Checking games data creation date...")

        gd_creation_date = datetime.strptime(self.library_data["date"], "%Y%m%dT%H%M%S")
        gd_days_since_last_update = (datetime.now() - gd_creation_date).days
        outdated = gd_days_since_last_update >= 2

        str_outdated = "needs update" if outdated else "ok"
        logger.debug("gamedetails.json created on: {}, age: {} days ({})".format(
                     gd_creation_date.strftime('%Y%m%d'), gd_days_since_last_update, str_outdated))

        if outdated:
            print("Games data is outdated. Updating...")
        else:
            print("Games data is up-to-date.")

        return outdated

    def get_game_info(self, game_name):
        """Get info associated with game from the library data.

        :param game_name: game name as stored in DownloadDir.
        :return: dicitionary with information associated with game_name.
        """
        for entry in self.games_list:
            if entry['gamename'] == game_name:
                logger.debug(f"Game info for {game_name} found")
                return entry

        logger.warning(f"Game info for {game_name} not found")
        return None
