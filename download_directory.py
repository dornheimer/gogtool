import logging
import os


logger = logging.getLogger(__name__)


class DownloadDir:
    def __init__(self, path):
        self.path = path
        self.files = self._scan_for_setup_files()

        logger.debug(f"{type(self).__name__} initialized with {self.path}")

    @property
    def games(self):
        return self.files.keys()

    def _scan_for_games(self):
        """Scan local download directory and return a list of downloaded games
        (folder names are game identifiers)."""
        logger.info("Scanning local directory for downloaded games...")
        return os.listdir(self.path)

    def _scan_for_setup_files(self):
        """Update files dictionary with setup files for each game."""
        logger.info("Scanning local directory for setup files...")
        files = {}
        for game_name in self._scan_for_games():
            game_path = os.path.join(self.path, game_name)
            game_files = os.listdir(game_path)
            setup_files, other_files = [], []
            setup_files = [gf for gf in game_files if gf.startswith(('gog', 'setup', game_name))]

            files[game_name] = {
                                "setup_files": setup_files,
                                "local_path": game_path
                                }
        return files

    def delete_files(self, game):
        """Delete all files of specified game."""
        logging.info(f"Deleting files for {game}")
        for fn in self.files[game.name]:
            file_path = os.path.join(self.path, game.name, fn)
            logger.debug(f"file_path for {game} is: {file_path}")
            print(file_path)
            #os.remove(file_path)
            logger.info(f"Removed {file_path}")
