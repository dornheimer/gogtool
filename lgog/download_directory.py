import os

from lgog.helper import system
from lgog.helper.directory import Directory
from lgog.helper.log import logger


class DownloadDir(Directory):
    """
    Store information about downloaded setup files.
    """
    def __init__(self, path):
        super().__init__(path)
        self.games = []
        self.setup_files = {}

    def _scan_for_games(self, game_library):
        """Scan local download directory and return a list of downloaded
        games.

        Gets called internally by scan_for_setup_files.

        :param game_library: list of games in GOG user library
        """
        dir_contents = os.listdir(self.path)
        self.games = [fp for fp in dir_contents if fp in game_library]

    def scan_for_setup_files(self, game_library):
        """Update files dictionary with setup files for each game."""
        self._scan_for_games(game_library)

        logger.info("Scanning local directory for setup files...")
        # 1. Check if file is on server
        # 2. Check if file name matches pattern

        setup_files = {}
        for game_name in self.games:
            game_path = os.path.join(self.path, game_name)
            game_files = os.listdir(game_path)

            prefixes = self._guess_prefixes(game_name)
            files = [gf for gf in game_files if gf.startswith(prefixes)]
            logger.debug(f"{len(files)} file(s) for {game_name} found")
            setup_files[game_name] = files

        self.setup_files = setup_files

    def delete_files(self, game):
        """Delete all files of specified game.

        :param Game game: A Game object.
        """
        print(f"Deleting files for {game.name}...")
        files = []
        for fn in self.get_files(game):
            file_path = os.path.join(self.path, game.name, fn)
            files.append(file_path)
        system.rm(files)

    def get_files(self, game_name):
        if game_name in self.games:
            try:
                local_files = self.setup_files[game_name]
            except KeyError:
                logger.warning(f"No entry for '{game_name}' in download directory",
                               exc_info=True)
                print(f"{game_name} not found in download directory. Skipping...")
                return None
            else:
                return local_files

    def get_path(self, game_name):
        if game_name not in self.games:
            return None

        game_path = os.path.join(self.path, game_name)
        if os.path.exists(game_path):
            return game_path
        else:
            logger.debug(f"Could not find '{game_name}' in download directory")
            return None

    def _guess_prefixes(self, game_name):
        prefixes = ['gog', 'setup', game_name]

        # Name has "_game" appended (tyranny_game)
        prefixes.append(game_name.split("_")[0])

        # Name separates letters and digits (tis100 -> tis_100)
        for i, char in enumerate(game_name):
            if not char.isalpha():
                prefixes.append(game_name[:i])
                break

        return tuple(prefixes)
