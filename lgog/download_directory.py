import os

from lgog.helper.log import logger


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

            alt_name = game_name.split("_")[0]
            prefixes = ('gog', 'setup', game_name, alt_name)
            setup_files = [gf for gf in game_files if gf.startswith(prefixes)]

            files[game_name] = {
                                "setup_files": setup_files,
                                "local_path": game_path
                                }
        return files

    def delete_files(self, game):
        """Delete all files of specified game."""
        logger.info(f"Deleting files for {game}")
        logger.debug(f"Local files for {game}: {game.local_path}")

        for fn in self.files[game.name]["setup_files"]:
            file_path = os.path.join(self.path, game.name, fn)
            logger.debug(f"file_path for {game} is: {file_path}")

            try:
                print(file_path)
                os.remove(file_path)
                logger.info(f"Removed {file_path}")
            except FileNotFoundError:
                logger.error("File path does not exist", exc_info=True)
