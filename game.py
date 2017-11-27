import logging
import os
import subprocess


logger = logging.getLogger(__name__)


class Game:
    def __init__(self, name, game_info, local_path):
        self.name = name
        self.game_info = game_info
        self.local_path = local_path
        self.installers = self._get_installers()
        self.dlc = self._get_dlc()
        self.update = False
        self.old_files = set()

    @property
    def local_files(self):
        file_names = os.listdir(self.local_path)
        game_name = self.name.split("_")[0]
        prefixes = ('gog', 'setup', self.name, game_name)

        return [fn for fn in file_names if fn.startswith(prefixes)]

    @property
    def platform(self):
        return 4 if 4 in self.installers else 1

    def _extract_from_game_info(self, key, platforms={4, 1}, id_prefix='en'):
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
        """Return installers for the game (linux and windows.)"""
        return self._extract_from_game_info("installers")

    def _get_dlc(self):
        """Return dlc for the game (linux and windows.)"""
        return self._extract_from_game_info("dlcs")

    def check_for_update(self):
        """Compare local files to those on the server."""
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

    def download(self):
        """Download newer versions of the game's setup files."""
        logger.debug(f"{self.name}.update == {self.update}")
        if self.update:
            if self.platform == 1:
                logger.debug(f"Platform for {self.name} is 'w'")
                update_args = ["lgogdownloader", "--platform", "w", "--download", "--game", self.name]
            if self.platform == 4:
                logger.debug(f"Platform for {self.name} is 'l'")
                update_args = ["lgogdownloader", "--download", "--game", self.name]

            logger.info(f'Downloading file(s) for {self.name}...')
            update_files = subprocess.Popen(update_args, stdout=subprocess.PIPE)
            stdout, _ = update_files.communicate()
            out = stdout.decode('utf-8')
            logger.info("Download complete")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"""{self.cls.__name__}({self.name}, {self.game_info}, {self.local_path})"""
