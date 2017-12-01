import os

from lgog.helper.directory import Directory
from lgog.helper.log import logger


class DownloadDir(Directory):
    """
    Store information about downloaded setup files.
    """
    def __init__(self, path):
        super().__init__(path)
        self.games = []
        self.files = {}

    def _scan_for_games(self, game_library):
        """Scan local download directory and return a list of downloaded
        games.

        Gets called internally by scan_for_setup_files.

        :param game_library: list of games in GOG user library
        """
        logger.info("Scanning local directory for downloaded games...")
        dir_contents = os.listdir(self.path)
        self.games = [fp for fp in dir_contents if fp in game_library]

    def scan_for_setup_files(self, game_library):
        """Update files dictionary with setup files for each game."""
        self._scan_for_games(game_library)

        logger.info("Scanning local directory for setup files...")

        files = {}
        for game_name in self.games:
            game_path = os.path.join(self.path, game_name)
            game_files = os.listdir(game_path)

            alt_name = game_name.split("_")[0]
            prefixes = ('gog', 'setup', game_name, alt_name)
            setup_files = [gf for gf in game_files if gf.startswith(prefixes)]
            files[game_name] = setup_files

        self.files = files

    def delete_files(self, game):
        """Delete all files of specified game.

        :param Game game: A Game object.
        """
        print(f"Deleting files for {game.name}...")
        for fn in self.get_files(game):
            file_path = os.path.join(self.path, game.name, fn)
            logger.debug(f"Trying to delete '{file_path}'")

            try:
                print(file_path)
                os.remove(file_path)
                logger.debug(f"Removed '{file_path}'")
            except FileNotFoundError:
                logger.error("File path does not exist", exc_info=True)

    def get_files(self, game_name):
        try:
            local_files = self.files[game_name]
            logger.debug(f"Local files for {game_name}: {local_files}")
        except KeyError:
            logger.warning(f"No entry for '{game_name}' in download directory",
                           exc_info=True)
            print("{game_name} not found in download directory. Skipping...")

        return local_files

    def get_path(self, game_name):
        if game_name in self.games:
            return os.path.join(self.path, game_name)
        else:
            try:
                raise FileNotFoundError
            except:
                logger.warning(f"Could not find '{game_name}' in download directory")
