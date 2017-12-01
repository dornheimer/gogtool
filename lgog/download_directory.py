import os

from lgog.helper.directory import Directory
from lgog.helper.log import logger


class DownloadDir(Directory):
    """
    Store information about downloaded setup files.
    """
    def __init__(self, path):
        super().__init__(path)
        self.files = self._scan_for_setup_files()

    @property
    def games(self):
        """Return a list of games in the download directory."""
        return self.files.keys()

    def _scan_for_games(self):
        """Scan local download directory and return a list of downloaded
        games.
        """
        logger.info("Scanning local directory for downloaded games...")
        return os.listdir(self.path)  # TODO: Compare against list of games

    def _scan_for_setup_files(self):
        """Update files dictionary with setup files for each game."""
        logger.info("Scanning local directory for setup files...")

        files = {}
        for game_name in self._scan_for_games():
            game_path = os.path.join(self.path, game_name)
            game_files = os.listdir(game_path)

            alt_name = game_name.split("_")[0]
            prefixes = ('gog', 'setup', game_name, alt_name)
            setup_files = [gf for gf in game_files if gf.startswith(prefixes)]

            files[game_name] = {"setup_files": setup_files,
                                "local_path": game_path}

        return files

    def delete_files(self, game):
        """Delete all files of specified game.

        :param Game game: A Game object.
        """
        print(f"Deleting files for {game}...")
        logger.debug(f"Local files for {game}: {game.local_path}")

        for fn in self.files[game.name]["setup_files"]:
            file_path = os.path.join(self.path, game.name, fn)
            logger.debug(f"Trying to delete '{file_path}'")

            try:
                print(file_path)
                os.remove(file_path)
                logger.debug(f"Removed '{file_path}'")
            except FileNotFoundError:
                logger.error("File path does not exist", exc_info=True)
