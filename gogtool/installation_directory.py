import os
import re

from .directory import Directory
from gogtool.helper.log import logger


class InstallDir(Directory):
    """Identifies and handles games in the local installation directory."""

    def __init__(self, local_library, path):
        super().__init__(path)
        self.local_library = local_library

    def scan_for_games(self):
        """Scan local installation directory for games and update their
        installation path if found.
        """
        logger.info("Scanning for installed games...")
        dir_contents = os.listdir(self.path)
        for game in self.local_library:
            install_names = self._guess_title_format(game.title)

            for iname in install_names:
                if iname in dir_contents:
                    logger.debug(f"{iname} found in installation directory")
                    install_path = os.path.join(self.path, iname)
                    game.install_path = install_path
                    break

    def delete_files(game):
        pass

    def has_uninstall_script(game):
        pass

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
