import os
import re

from gogtool.helper.directory import Directory
from gogtool.helper.log import logger


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
            install_names = self._convert_title_format(game.title)

            for iname in install_names:
                if iname in dir_contents:
                    logger.debug(f"{iname} found in installation directory")
                    game_name = game.gamename
                    install_path = os.path.join(self.path, game_name)
                    # Use "gamename" as identifier for consistency
                    self.installed_games_dict[game_name] = iname, install_path
                    break

    def initialize_game(self, game):
        if game.name in self.installed_games_dict:
            game.installed = True
            game.install_path = self.get_path(game.name)

    # TODO: manage save games
    # TODO: connect to lutris?

    def _convert_title_format(self, game_title):
        install_names = []

        # Convert titles with special chars and replace consecutive spaces
        # with a single space
        special_chars = re.compile(r"[^a-zA-Z0-9 ]")
        no_specials = special_chars.sub(" ", game_title)
        multiple_spaces = re.compile(r"\s{2,}")
        install_name = multiple_spaces.sub(" ", no_specials)
        install_names.append(install_name)

        install_name_alt = game_title.replace("_", "-")
        install_names.append(install_name_alt)

        install_name_alt1 = game_title.replace(":", "-")
        install_names.append(install_name_alt1)

        return install_names

    def get_path(self, game_name):
        return self.installed_games_dict[game_name][1]
