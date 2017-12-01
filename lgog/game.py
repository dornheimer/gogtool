import os

import lgog.helper.lgogdownloader as lgogdownloader
from lgog.helper.log import logger


class Game:
    """
    Data and methods related to a single game in the library.
    """
    def __init__(self, name, game_info, local_path, local_files):
        self.name = name
        self.game_info = game_info
        self.local_path = local_path
        self.local_files = local_files

        self.installers = self._get_installers()
        self.dlc = self._get_dlc()
        self.update = False
        self.conf = False
        self.old_files = set()

    @property
    def platform(self):
        """Set platform to linux if available.

        Note:
            4=linux, 1=windows
        """
        return 4 if 4 in self.installers else 1

    def _extract_from_game_info(self, key, id_prefix='en'):
        """Get item from game_info dictionary.

        :param key: dictionary key of the item.
        :param id_prefix: language identifier string (default='en').
        """
        platforms = {4, 1}
        values = {}
        try:
            for v in self.game_info[key]:
                if v['platform'] in platforms and v['id'].startswith(id_prefix):
                    values.setdefault(v['platform'], []).append(v['path'])
            logger.debug(f"{key} found for {self.name}")
            return values

        except KeyError:
            logger.debug(f"No {key} for {self.name} found")
            return None

    def _get_installers(self):
        return self._extract_from_game_info("installers")

    def _get_dlc(self):
        return self._extract_from_game_info("dlcs")

    def check_for_update(self):
        """Compare local file versions to those on the server.

        Result is stored in self.update.

        :return: True or False
        """
        logger.info(f"Checking {self.name} for updates...")

        server_path = self.installers[self.platform]
        logger.debug(f"Server path for {self.name} is: {''.join(server_path)}")

        server_files = [os.path.basename(sp) for sp in server_path]
        logger.debug(f"Local files for {self.name}: {', '.join(self.local_files)}")
        if not all([(sf in self.local_files) for sf in server_files]):
            self.update = True
            old = [lf for lf in self.local_files if lf not in server_files]
            self.old_files.update(old)

        return self.update

    def download(self, file_id=None):
        """Download setup files for game.

        :param file_id: optionally download file by ID instead.
        """
        if file_id is not None:
            lgogdownloader.download(self.name, file_id)
        else:
            lgogdownloader.download(self.name, self.platform)

    def update_game(self):
        """Download newer versions of the game's setup files."""
        logger.debug(f"{self.name}.update == {self.update}")
        if self.update:
            self.download()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"""{self.cls.__name__}({self.name}, {self.game_info}, {self.local_path})"""
