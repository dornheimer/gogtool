import os
import itertools

from .directory import Directory
from gogtool.helper import system
from gogtool.helper.log import logger


class DownloadDir(Directory):
    """Identifies and handles games in the local download directory."""

    def __init__(self, local_library, path):
        super().__init__(path)
        self.local_library = local_library

    def scan_for_games(self):
        """Scan local download directory for games in the library.

        Maps game_name to (download_path, setup_files) in self._games.

        :param game_library: GOG user library (a LibraryData object)
        """
        logger.info("Scanning for downloaded games...")
        dir_contents = os.listdir(self.path)

        for game in self.local_library:
            if game.name in dir_contents:
                self._scan_for_setup_files(game)

    def _scan_for_setup_files(self, game):
        """Look for a game's setup files in its download folder.

        :param game: A Game object.
        :param download_path: Download folder of the game
        :return: A list of the recognized setup files.
        """
        download_path = os.path.join(self.path, game.name)
        local_files = os.listdir(download_path)
        server_files = itertools.chain.from_iterable(game.setup_files.values())
        server_files = [str(file_) for file_ in server_files]
        prefixes = self._guess_prefixes(game.name)

        for lf in local_files:
            if lf in server_files:
                game.current_files.add(lf)
            if lf.startswith(prefixes) and lf not in server_files:
                game.old_files.add(lf)

        game.download_path = download_path
        game.downloaded = True
        if game.current_files or game.old_files:
            logger.debug(f"Setup file(s) for {game.name} found")
        else:
            logger.debug(f"Empty folder for {game.name} found")

    def is_empty_folder(self, game):
        return not game.current_files | game.old_files

    def delete_files(self, game):
        """Delete old files of specified game.

        :param game: A Game object.
        """
        print(f"Deleting files for {game.name}...")
        for file_name in game.old_files:
            file_path = os.path.join(game.download_path, file_name)
            system.rm(file_path)

        game.old_files = None

    def _guess_prefixes(self, game_name):
        """Guess prefix of the setup file.

        :param game_name: Game name as found in the GOG library data.
        :return: A tuple with prefix strings.
        """
        prefixes = ['gog', 'setup', game_name]

        # Name has "_game" appended (tyranny_game)
        prefixes.append(game_name.split("_")[0])

        # Name separates letters and digits (tis100 -> tis_100)
        for i, char in enumerate(game_name):
            if not char.isalpha():
                prefixes.append(game_name[:i])
                break

        return tuple(prefixes)

    def check_outdated(self, game, include_empty=False):
        if not include_empty:
            if not self.is_empty_folder(game):
                outdated = not game.current_files
                if outdated:
                    logger.debug("{} needs update: {}".format(
                        game.name, outdated))
            else:
                outdated = False
        else:
            outdated = not game.current_files
            if outdated:
                logger.debug("{} needs update: {}".format(
                    game.name, outdated))

        return outdated
