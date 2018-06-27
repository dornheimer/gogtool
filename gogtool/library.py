import logging
import os
from datetime import datetime
from operator import attrgetter, itemgetter

from gogtool import gogdb
from gogtool import util
from gogtool.game import Game

logger = logging.getLogger(__name__)


class Library:
    def __init__(self, gog_library, config):
        self.gog_library = gog_library
        self.config = config
        self.gog_db = gogdb.GOGDB()

        self.download_dir = config['download_dir']
        self.install_dir = config['install_dir']
        self.gog_games = sorted(
            [g for g in gog_library['games']], key=itemgetter('gamename')
        )
        self._games = {}

        self.scan_download_dir()
        self.scan_install_dir()

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}({type(self).is_outdated()})"

    def get_all_games(self):
        return (self.get_game(g['gamename']) for g in self.gog_games)

    @property
    def local_games(self):
        return sorted(self._games.values(), key=attrgetter('name'))

    @property
    def downloaded_games(self):
        return [g for g in self.local_games if g.is_downloaded]

    @property
    def installed_games(self):
        return [g for g in self.local_games if g.is_installed]

    @property
    def installed_dlcs(self):
        return [
            [dlc for dlc in ig.installable_dlcs if dlc.is_installed]
            for ig in self.installed_games
        ]

    @property
    def outdated_games(self):
        return [g for g in self.local_games if g.needs_update]

    def get_all_values(self, key):
        return [g[key] for g in self.gog_library['games']]

    def _get_game_data(self, game_name):
        for game_data in self.gog_library['games']:
            if game_data['gamename'] == game_name:
                return game_data

    def get_game(self, game_name, **kwargs):
        try:
            game = self._games[game_name]
            for attr, value in kwargs.items():
                setattr(game, attr, value)
        except KeyError:
            game_data = self._get_game_data(game_name)
            game = Game(game_data, **kwargs)
            game_image_id = self.gog_db.get_game_img(game_name)
            game.image_url = self.make_img_url(game_image_id)
            self._games[game_name] = game
        return game

    def find_games(self):
        logger.debug(
            "Looking for for downloaded games in: %s", self.download_dir
        )
        game_subdir_fmt = self.config['lgogdownloader']['subdir-game']
        logger.debug('Game subdir format is: %s', game_subdir_fmt)
        game_names = self.get_all_values('gamename')
        for item in os.listdir(self.download_dir):
            item_path = os.path.join(self.download_dir, item)
            if game_subdir_fmt == '%gamename%':
                if not (os.path.isdir(item_path) and item in game_names):
                    continue
                game = self.get_game(game_name=item, download_dir=item_path)

                if game.has_dlc:
                    self.find_dlcs(game)
                if game.has_patches:
                    self.find_patches(game)

    def find_dlcs(self, game):
        dlc_subdir_fmt = self.config['lgogdownloader']['subdir-dlc']
        dlc_subdir, dlc_id = dlc_subdir_fmt.split('/')
        dlc_dir = os.path.join(game.download_dir, dlc_subdir)
        if not os.path.exists(dlc_dir):
            return
        for x in os.listdir(dlc_dir):
            if dlc_id == '%dlcname%':
                if x not in game.installable_dlcs:
                    continue
                dlc = game.installable_dlcs[x]
                dlc.download_dir = os.path.join(dlc_dir, x)
                dlc.downloaded_files = dlc.find_downloaded_files()

    def find_patches(self, game):
        pass

    def scan_download_dir(self):
        logger.debug(
            "Looking for for downloaded games in: %s", self.download_dir
        )
        game_subdir_fmt = self.config['lgogdownloader']['subdir-game']
        logger.debug('Game subdir format is: %s', game_subdir_fmt)
        game_names = self.get_all_values('gamename')
        for item in os.listdir(self.download_dir):
            item_path = os.path.join(self.download_dir, item)
            if game_subdir_fmt == '%gamename%':
                if not (os.path.isdir(item_path) and item in game_names):
                    continue
                game = self.get_game(game_name=item, download_dir=item_path)

                if game.has_dlc:
                    self.find_dlcs(game)

        # TODO: look for patches

    def scan_install_dir(self):
        logger.debug(
            "Looking for for installed games in: %s", self.install_dir
        )
        game_names = self.get_all_values('gamename')
        game_titles = self.get_all_values('title')
        for item in os.listdir(self.install_dir):
            item_path = os.path.join(self.install_dir, item)
            for gn, gt in zip(game_names, game_titles):
                if os.path.isdir(item_path) and item in (gn, gt):
                    # Refer to games by 'gamename'
                    self.get_game(game_name=gn, install_dir=item_path)
                    break

    def download(self, game_name):
        logger.info("Downloading %s", game_name)
        game = self.get_game(game_name)
        game.download(self.download_dir)

    def install(self, game_name):
        logger.info("Installing %s", game_name)
        game = self.get_game(game_name)
        game.install(self.install_dir, self.download_dir)

    def update(self, game_name):
        game = self.get_game(game_name)
        game.update()

    def uninstall(self, game_name):
        logger.info("Uninstalling %s", game_name)
        game = self.get_game(game_name)
        game.uninstall()

    def delete_setup_files(self, game_name):
        game = self.get_game(game_name)
        game.delete_setup_files()

    def remove(self, game_name):
        logger.info("Removing %s", game_name)
        game = self.get_game(game_name)
        game.remove()

    def view_install_dir(self, game_name):
        game = self.get_game(game_name)
        logger.info("Open %s", game.install_dir)
        game.view_install_dir()

    def run(self, game_name):
        game = self.get_game(game_name)
        logger.info("Launching %s", game_name)
        game.run()

    def check_orphaned(self):
        orphans = []
        for game in self.downloaded_games:
            current, orphan = game.match_server_files()
            if orphan:
                orphans.extend(list(orphan))
        return orphans

    def delete_orphaned_files(self):
        orphaned_files = self.check_orphaned()
        for file_path in orphaned_files:
            print(file_path)
        if util.user_confirm("Delete orphaned files?"):
            util.rm_all(orphaned_files)

    def make_img_url(self, image_id):
        host_num = hash(image_id) % 4 + 1
        return f'https://images-{host_num}.gog.com/{image_id}_196.jpg'

    @staticmethod
    def is_outdated(gog_library):
        date_str = gog_library['date']
        creation_date = datetime.strptime(date_str, "%Y%m%dT%H%M%S")
        days_since_last_update = (datetime.now() - creation_date).days
        outdated = (days_since_last_update >= 2)

        outdated_str = "outdated" if outdated else "up-to-date"
        logger.info("Library data is %s", outdated_str)
        return (days_since_last_update >= 2)
