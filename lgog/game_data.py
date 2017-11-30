from datetime import datetime
import logging
import json
import sys

from lgog.helper.log import logger


class GameData:
    def __init__(self, path):
        self.path = path
        self.games_data = self._get_games_data()
        self.games_list = self.games_data["games"]

        logger.debug(f"{type(self).__name__} initialized with {self.path}")

    def _get_games_data(self):
        """Get games data from lgogdownloader json file."""
        try:
            with open(self.path) as data:
                games_data = json.load(data)
        except FileNotFoundError:
            logger.error(f"Game details data not found in {self.path}", exc_info=True)
            sys.exit()

        logger.debug(f"Game details data found in {self.path}")
        return games_data

    @property
    def is_outdated(self):
        """Check if creation timestamp of game details is older than two days."""
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

    def get_game_info(self, game):
        for title in self.games_list:
            if title['gamename'] == game:

                logger.debug(f"Game info for {game} found")
                return title

        logger.warning(f"Game info for {game} not found")
        return None
