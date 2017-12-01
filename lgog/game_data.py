from datetime import datetime
import json

from lgog.helper.directory import Directory
from lgog.helper.log import logger


class GameData(Directory):
    """
    User-specific GOG library data.
    """
    def __init__(self, path):
        super().__init__(path)
        self.games_data = self._get_games_data()
        self.games_list = self.games_data["games"]

    def _get_games_data(self):
        """Convert gamedetails.json file into a python dictionary."""
        with open(self.path) as data:
            games_data = json.load(data)

        return games_data

    @property
    def is_outdated(self):
        """Check if game details file is older than two days."""
        logger.info("Checking games data creation date...")

        gd_creation_date = datetime.strptime(self.games_data["date"], "%Y%m%dT%H%M%S")
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
        for title in self.games_list:
            if title['gamename'] == game_name:
                logger.debug(f"Game info for {game_name} found")
                return title

        logger.warning(f"Game info for {game_name} not found")
        return None
