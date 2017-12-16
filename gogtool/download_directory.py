import os

from gogtool.helper import user
from gogtool.helper import system
from gogtool.helper.directory import Directory
from gogtool.helper.log import logger


class DownloadDir(Directory):
    """
    Store information about downloaded setup files.
    """

    def scan_for_games(self, game_library):
        """Scan local download directory for games in the library.

        Maps game_name to (download_path, setup_files) in self._games.

        :param game_library: GOG user library (a LibraryData object)
        """
        logger.info("Scanning for downloaded games...")
        dir_contents = os.listdir(self.path)

        for game in game_library:
            game_name = game.gamename
            if game_name in dir_contents:
                download_path = os.path.join(self.path, game_name)
                setup_files = self._scan_for_setup_files(game_name, download_path)
                self._games[game_name] = download_path, setup_files

    def _scan_for_setup_files(self, game_name, download_path):
        """Look for a game's setup files in its download folder.

        :param game_name: Name of the game
        :param download_path: Download folder of the game
        """
        logger.info("Scanning local directory for setup files...")
        game_files = os.listdir(download_path)
        prefixes = self._guess_prefixes(game_name)
        setup_files = [gf for gf in game_files if gf.startswith(prefixes)]
        logger.debug(f"{len(setup_files)} file(s) for {game_name} found")

        return setup_files

    def initialize_game(self, game):
        """Pass information of game to its Game object.

        If an empty folder was found, ask if latest installer should be
            downloaded.

        :param game: A Game object.
        """
        if game.name not in self._games:
            download_path, setup_files = None, None
        else:
            download_path, setup_files = self[game.name]

        if setup_files is not None:
            if not setup_files:  # Empty folder
                prompt = (f"Folder for {game} is empty. Download latest installer?")
                if user.confirm(prompt):
                    game.download = True
                    game.conf = True
            else:
                game.downloaded = True

        game.download_path = download_path
        game.download_files = setup_files

    def delete_files(self, game):
        """Delete all files of specified game.

        :param game: A Game object.
        """
        print(f"Deleting files for {game.name}...")
        download_path, setup_files = self[game.name]

        files = []
        for file_name in setup_files:
            file_path = os.path.join(download_path, file_name)
            files.append(file_path)
        system.rm(files)

    def _guess_prefixes(self, game_name):
        """Guess prefix of the setup file.

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
