import os

from gogtool.game import Game
from gogtool.helper import user
from gogtool.helper.log import logger


class LocalLibrary:
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

    @property
    def downloaded_games(self):
        return [game for game in self.games.values() if game.downloaded]

    @property
    def installed_games(self):
        return [game for game in self.games.values() if game.installed]

    @property
    def games_with_update(self):
        return [game for game in self.games.values() if game.needs_update]

    @property
    def download_queue(self):
        return [game for game in self.games.values() if game.download]

    def _add_games(self):
        """Populate the library with all games in the user's GOG library.

        Games receive their data from LibraryData. DownloadDir and InstallDir
        look for the game and update its attributes accordingly.
        """
        for game in self.library_data.games:
            game_data = self.library_data.get_game_data(game)
            game_object = Game(game_data)

            self.download_dir.initialize_game(game_object)
            self.install_dir.initialize_game(game_object)
            self.games[game] = game_object

        print("{} games in GOG library".format(self.library_data.size))
        print("{} downloaded".format(len(self.downloaded_games)))
        print("{} installed".format(len(self.installed_games)))

    def _check_for_updates(self):
        """Check every downloaded game for available updates."""
        logger.info("Checking for updates...")
        for game in self.downloaded_games:
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

        Note:
            Path is path_to_install_dir/gog_id/

        :param game_name: Name of the game as found in the library data.
        :param platform: Platform of the installer (1 = Windows, 2 = MacOS,
            4 = Linux)
        """
        logger.debug(f"Installing {game_name}...")
        game = self.games.get(game_name)
        dest = os.path.join(self.install_dir.path, game.name)
        game.install(dest, platform)
