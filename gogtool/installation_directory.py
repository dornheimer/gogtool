import os
import re

from gogtool.helper.directory import Directory
from gogtool.helper.log import logger


class InstallDir(Directory):
    """
    Store information about installed GOG games.
    """

    def scan_for_games(self, game_library):
        """Scan local installation directory and add game to class dictionary if
        found.

        Maps game_name to install_path in self._games.

        :param game_library: GOG user library (a LibraryData object)
        """
        logger.info("Scanning for installed games...")
        dir_contents = os.listdir(self.path)
        for game in game_library:
            install_names = self._guess_title_format(game.title)

            for iname in install_names:
                if iname in dir_contents:
                    logger.debug(f"{iname} found in installation directory")
                    install_path = os.path.join(self.path, iname)
                    self._games[game.gamename] = install_path
                    break

    def initialize_game(self, game):
        """Pass information of game to its Game object.

        :param game: A Game object.
        """
        if game.name in self._games:
            game.installed = True
            game.install_path = self[game.name]

    def _guess_title_format(self, game_title):
        """Guess the name of the installation directory of the game (based on
        its title).
        """
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
