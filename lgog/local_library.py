from lgog.game import Game
from lgog.helper import user
from lgog.helper.log import logger


class LocalLibrary:
    def __init__(self, library_data, download_dir, install_dir):
        self.library_data = library_data
        self.download_dir = download_dir
        self.install_dir = install_dir
        self.games = []

        self._add_games()
        self._check_for_updates()

    @property
    def downloaded_games(self):
        return [game for game in self.games if game.downloaded]

    @property
    def installed_games(self):
        return [game for game in self.games if game.installed]

    @property
    def games_with_update(self):
        return [game for game in self.games if game.needs_update]

    @property
    def download_queue(self):
        return [game for game in self.games if game.download]

    def _add_games(self):
        for game in self.library_data.games:
            game_info = self.library_data.get_game_info(game)
            local_path = self.download_dir.get_path(game)
            local_files = self.download_dir.get_files(game)
            game_object = Game(game, game_info, local_path, local_files)

            if local_files is not None:
                if local_files == []:  # Empty folder
                    prompt = (f"Folder for {game} is empty. Download latest installer?")
                    if user.confirm(prompt):
                        game_object.download = True
                        game_object.conf = True
                else:
                    game_object.downloaded = True

            self.games.append(game_object)
        print(f"{self.library_data.size} games in GOG library")
        print(f"{len(self.downloaded_games)} downloaded")
        print(f"{len(self.installed_games)} installed")

    def _check_for_updates(self):
        logger.info("Checking for updates...")
        names = [g.name for g in self.downloaded_games]
        logger.debug(f"Downloaded games: {', '.join(names)}")
        for game in self.downloaded_games:
            game.check_for_update()

        print("\nGames with outdated setup files:")
        print("\n".join([g.name for g in self.games_with_update]), end="\n\n")
        logger.debug(f"{len(self.games_with_update)} games with updates")

    def update_games(self, download_all=False, delete_by_default=False):
        # Ask for download confirmation by default
        for game in self.games_with_update:
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
