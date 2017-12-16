from collections.abc import Mapping
import os

from gogtool.game import Game
from gogtool.helper import user
from gogtool.helper.log import logger


class LocalLibrary(Mapping):
    """
    Aggregates all available data and keeps track of every game in the library.
    """
    def __init__(self, library_data, download_dir, install_dir):
        self.library_data = library_data
        self.download_dir = download_dir
        self.install_dir = install_dir
        self.games = {}

        self._add_games()
        self._check_for_updates()

    def __len__(self):
        return len(self.games)

    def __getitem__(self, game_name):
        if game_name not in self.games:
            try:
                raise KeyError
            except KeyError:
                logger.debug(f"Could not find '{game_name}' in {type(self).__name__}")
                return None
        return self.games[game_name]

    def __iter__(self):
        return iter(self.games.values())

    @property
    def games_with_update(self):
        return [game for game in self if game.needs_update]

    @property
    def download_queue(self):
        return [game for game in self if game.download]

    def _add_games(self):
        """Populate the library with all games in the user's GOG library.

        Games receive their data from LibraryData. DownloadDir and InstallDir
        look for the game and update its attributes accordingly.
        """
        for game_data in self.library_data:
            game = Game(game_data)

            self.download_dir.initialize_game(game)
            self.install_dir.initialize_game(game)
            self.games[game.name] = game

        print("{} games in GOG library".format(len(self.library_data)))
        print("{} downloaded".format(len(self.download_dir)))
        print("{} installed".format(len(self.install_dir)))

    def _check_for_updates(self):
        """Check every downloaded game for available updates."""
        logger.info("Checking for updates...")
        for game_name in self.download_dir:
            game = self[game_name]
            game.check_for_update()

        print("\nGames with outdated setup files:")
        print("\n".join([g.name for g in self.games_with_update]), "\n")
        logger.debug("%s games with updates", len(self.games_with_update))

    def update_games(self, download_all=False, delete_by_default=False):
        """Update games with outdated setup files.

        :param download_all: Download every game, do not ask for confirmation.
        :param delete_by_default: Do not ask for confirmation before deleting.
        """
        if not download_all:
            for game in self.games_with_update:
                # Check if user already made a choice
                if game.conf:
                    continue
                # Unselect game if user reponse is "no"
                prompt = f"Re-download file(s) for {game.name}?"
                if not user.confirm(prompt):
                    game.download = False
                    game.conf = True

        for game in self.download_queue:
            game.update_game()

        delete = delete_by_default
        if not delete_by_default:
            prompt = "Delete old setup files?"
            if user.confirm(prompt):
                delete = True

        if delete:
            print("Deleting files...")
            for game in self.download_queue:
                    self.download_dir.delete_files(game)

    def install_game(self, game_name, platform=4):
        """Install game into installation directory.

        Path is install_dir/game_name/ or install_dir/install_name (if game is
        already installed).

        :param game_name: Name of the game as found in the library data.
        :param platform: Platform of the installer (1 = Windows, 2 = MacOS,
            4 = Linux)
        """
        logger.debug(f"Installing {game_name}...")
        game = self[game_name]

        # Check if game is already installed and define destination path with
        # trailing separator
        if game.installed and game.install_path is not None:
            dest = os.path.join(game.install_path, "")
            logger.debug(f"{game.name} is installed in {game.install_path}")
        else:
            dest = os.path.join(self.install_dir.path, game.name, "")

        game.install(dest, platform)
