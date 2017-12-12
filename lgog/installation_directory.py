import os
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
        for game in game_library.games.values():
            game_name = game.gamename
            install_name = self._convert_title_format(game.title)
            install_name_alt = game_name.replace("_", "-")
            if install_name in dir_contents or install_name_alt in dir_contents:
                logger.debug(f"{install_name} found in installation directory")
                install_path = os.path.join(self.path, game_name)
                # Use "gamename" as identifier for consistency
                self.installed_games_dict[game_name] = install_name, install_path

    def initialize_game(self, game):
        if game.name in self.installed_games_dict:
            game.installed = True
            game.install_path = self.get_path(game.name)

    # manage save games??
    # connect to lutris??
    def _convert_title_format(self, game_title):
        # TODO: : is sometimes replaced with -
        special_chars = re.compile(r"[^a-zA-Z0-9 ]")
        no_specials = special_chars.sub(" ", game_title)
        multiple_spaces = re.compile(r"\s{2,}")
        install_name = multiple_spaces.sub(" ", no_specials)

        return install_name

    def get_path(self, game_name):
        return self.installed_games_dict[game_name][1]
