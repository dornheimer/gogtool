import os

from .directory import Directory
from gogtool.helper import user
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
                download_path = os.path.join(self.path, game.name)

                setup_files = self._scan_for_setup_files(game.name, download_path)
                if not setup_files:  # Empty folder
                    prompt = (f"Folder for {game} is empty. Download latest installer?")
                    if user.confirm(prompt):
                        game.download = True
                        game.conf = True

                game.download_path = download_path
                game.download_files = setup_files

    def _scan_for_setup_files(self, game_name, download_path):
        """Look for a game's setup files in its download folder.

        :param game_name: Name of the game
        :param download_path: Download folder of the game
        :return: A list of the recognized setup files.
        """
        logger.info("Scanning local directory for setup files...")
        game_files = os.listdir(download_path)
        prefixes = self._guess_prefixes(game_name)
        setup_files = [gf for gf in game_files if gf.startswith(prefixes)]
        logger.debug(f"{len(setup_files)} file(s) for {game_name} found")

        return setup_files

    def delete_files(self, game):
        """Delete all files of specified game.

        :param game: A Game object.
        """
        print(f"Deleting files for {game.name}...")
        files = []
        for file_name in game.download_files:
            file_path = os.path.join(game.download_path, file_name)
            files.append(file_path)
        system.rm(files)
        game.download_files = None

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
