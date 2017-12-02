import os
import subprocess
import re

from lgog.helper.directory import Directory
from lgog.helper.log import logger


class InstallDir(Directory):
    """
    Store information about installed GOG games.
    """
    def __init__(self, path):
        super().__init__(path)
        self.installed_games_dict = {}

    @property
    def installed_games(self):
        return list(self.installed_games_dict.keys())

    def scan_for_games(self, game_library):
        """Scan local installatin directory and return a list of installed
        games.

        :param game_library: GOG user library
        """
        logger.info("Scanning for installed games...")
        dir_contents = os.listdir(self.path)
        for game in game_library.games_list:
            game_name = game["gamename"]
            install_name = self._convert_title_format(game["title"])
            if install_name in dir_contents:
                logger.debug(f"{install_name} found in installation directory.")
                # Use "gamename" as identifier for consistency
                self.installed_games_dict[game_name] = install_name

        logger.debug(f"Installed games: {', '.join(self.installed_games)}")

    # manage save games??
    # connect to lutris??
    def _convert_title_format(self, game_title):
        # TODO: : is sometimes replaced with -
        special_chars = re.compile(r"[^a-zA-Z0-9 ]")
        no_specials = special_chars.sub(" ", game_title)
        multiple_spaces = re.compile(r"\s{2,}")
        install_name = multiple_spaces.sub(" ", no_specials)
        logger.debug(f"Install name for {game_title} is: {install_name}")

        return install_name

    def install(self, game):
        # install/update (extract) downloaded installers here
        # innoextract
