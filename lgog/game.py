import os
import subprocess

from lgog.helper.log import logger


class Game:
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
        """Compare local file versions to those on the server."""
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
        """Download setup files for game (optionally by file ID)."""
        lgog_args = ["lgogdownloader"]

        if file_id is not None:
            # Format: 'gamename/file_id'
            lgog_args.extend(["download-file", f"{self.name}/{file_id}"])
        else:
            if self.platform == 1:
                logger.debug(f"Platform for {self.name} is 'w'")
                lgog_args.extend(["--platform", "w", "--download", "--game", self.name])
            if self.platform == 4:
                logger.debug(f"Platform for {self.name} is 'l'")
                lgog_args.extend(["--download", "--game", self.name])

        print(f'Downloading file(s) for {self.name}...')
        logger.debug(f"Executing: {', '.join(lgog_args)}")
        download_files = subprocess.Popen(lgog_args, stdout=subprocess.PIPE)
        stdout, _ = download_files.communicate()
        out = stdout.decode('utf-8')
        print("Download complete")

    def update_game(self):
        """Download newer versions of the game's setup files."""
        logger.debug(f"{self.name}.update == {self.update}")
        if self.update:
            self.download()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"""{self.cls.__name__}({self.name}, {self.game_info}, {self.local_path})"""
