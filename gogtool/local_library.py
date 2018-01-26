from collections.abc import Mapping
import os

from .installation_directory import InstallDir
from .download_directory import DownloadDir
from gogtool.game import Game
from gogtool.helper import user
from gogtool.helper.log import logger


class LocalLibrary(Mapping):
    """
    Aggregates all available data and keeps track of every game in the library.
    """

    def __init__(self, library_data, download_path, install_path, include_empty):
        self.library_data = library_data
        self.include_empty = include_empty
        self.download_dir = DownloadDir(self, download_path)
        self.install_dir = InstallDir(self, install_path)
        self.games = {}

        self._add_games()
        self.download_dir.scan_for_games()
        self.install_dir.scan_for_games()
        self._check_for_updates()

    def __len__(self):
        return len(self.games)

    def __getitem__(self, game_name):
        if game_name not in self.games:
            try:
                raise KeyError
            except KeyError:
                logger.debug(
                    f"Could not find '{game_name}' in {type(self).__name__}")
        return self.games[game_name]

    def __iter__(self):
        return iter(self.games.values())

    @property
    def games_with_update(self):
        return [game for game in self if game.needs_update]

    @property
    def downloaded_games(self):
        return [game for game in self if game.downloaded]

    @property
    def installed_games(self):
        return [game for game in self if game.installed]

    @property
    def download_queue(self):
        return [game for game in self if game.download]

    def _add_games(self):
        """Populate the library with all games in the user's GOG library.

        Create a Game object for every entry in the user's GOG library and map
        it to its name.
        """
        for game_data in self.library_data:
            game = Game(game_data)
            self.games[game.name] = game

    def _check_for_updates(self):
        """Check every downloaded game for available updates.

        Assumes that the version of the installer in the download directory is
        also the version of the installed game.
        """
        logger.info("Checking for updates...")
        for game in self.downloaded_games:
            game.needs_update = self.download_dir.check_outdated(game, self.include_empty)

            if self.include_empty and self.download_dir.is_empty_folder(game):
                prompt = (f"Folder for {game} is empty. Download latest installer?")
                if user.confirm(prompt):
                    game.download = True
                    game.conf = True

        self.print_list('outdated')

    def update_games(self, download_all=False, delete_by_default=False):
        """Update games with outdated setup files.

        :param download_all: Download every game, do not ask for confirmation.
        :param delete_by_default: Do not ask for confirmation before deleting
            old setup files.
        """
        self.print_info()
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
            game.update()

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

    def uninstall_game(self, game_name):
        """Uninstall game from install directory."""
        logger.debug(f"Uninstalling {game_name}...")
        try:
            game = self[game_name]
        except KeyError:
            print(f"{game_name} not found in library. Skipping...")
        else:
            if game in self.installed_games:
                game.uninstall()
            else:
                logger.warning(f"{game_name} is not installed")

    def download_game(self, game_name, delete_old=False):
        """Download setup files for a game.

        :param game_name: Game name as found in the GOG library data.
        :param delete_old: Delete old files after downloading.
        """
        logger.debug(f"Downloading {game_name}...")
        try:
            game = self[game_name]
        except KeyError:
            print(f"{game_name} not found in library. Skipping...")
        else:
            game.download_setup_files()

        if delete_old:
            self.download_dir.delete_files(game)

    def print_info(self):
        """Print summary of local library information."""
        print("{} games in GOG library".format(len(self.library_data)))
        print("{} downloaded".format(len(self.downloaded_games)))
        print("{} installed".format(len(self.installed_games)))

    def print_list(self, category):
        """Print a list of games in category as column.

        Possible categories are: 'installed', 'downloaded', and 'outdated'

        :param category: List to print
        """
        categories = {
            "installed": (self.installed_games, "No games installed."),
            "downloaded": (self.downloaded_games, "No games downloaded."),
            "outdated": (self.games_with_update, "All games are up-to-date.")
        }

        games, empty_list_str = categories[category]
        if games:
            game_names = [str(game) for game in games]
            desc = f" {category} games "
            print("{:*^40}".format(desc))
            print("\n".join(game_names))
        else:
            print("\n{}".format(empty_list_str))

    def clean(self):
        """Delete outdated setup files for all games."""
        print("Cleaning outdated setup files...")
        for game in self.games_with_update:
            self.download_dir.delete_files(game)
