import os
import sys

import gogtool.helper.lgogdownloader as lgogdownloader
from gogtool.helper import user
from gogtool.helper import run
from gogtool.helper import system
from gogtool.helper.log import logger


class Game:
    """
    Data and methods related to a single game in the library.
    """
    def __init__(self, game_data):
        self.game_data = game_data

        self.name = None
        self.setup_files = {}
        self.installers = {}
        self.dlcs = {}

        self.downloaded = False
        self.download_path = None
        self.download_files = None

        self.installed = False
        self.install_path = None

        self.needs_update = False
        self.download = False
        self.conf = False
        self.old_files = []

        self._get_game_data()

    @property
    def available_platforms(self):
        return list(self.game_data.setup_files)

    @property
    def platform(self):
        """Set platform to linux if available.

        Note:
            4=linux, 1=windows, 2=mac
        """
        if 4 in self.available_platforms:
            return 4
        elif 1 in self.available_platforms:
            return 1
        elif 2 in self.available_platforms:
            return 2

    @property
    def has_dlc(self):
        return self.game_data.dlcs != {}

    def _get_game_data(self):
        self.name = self.game_data.gamename
        self.setup_files = self.game_data.setup_files
        self._get_installers()
        self.dlcs = self.game_data.dlcs

    def _get_installers(self, id_prefix='en'):
        # Some games have multiple setup files and only one executable installer
        for platform, installers in self.setup_files.items():
            for inst in installers:
                if inst.file_name.endswith((".exe", ".sh", ".dmg")):
                    self.installers[platform] = inst.file_name
                    break

    def check_for_update(self):
        """Compare local file versions to those on the server.

        Result is stored in self.update.

        :return: True or False
        """
        installers_server = self.setup_files[self.platform]
        inst_filenames = [i.file_name for i in installers_server]

        same_files = all([(fn in self.download_files) for fn in inst_filenames])
        logger.debug(f"{self.name}: downloaded files match server_files ({same_files})")
        if not same_files:
            self.needs_update = True
            self.old_files = self.download_files

    def download_setup_files(self, file_id=None):
        """Download setup files for game.

        :param file_id: optionally download file by ID instead.
        """
        if file_id is not None:
            lgogdownloader.download(self.name, file_id)
        else:
            lgogdownloader.download(self.name, self.platform)

        self.downloaded = True

    def update_game(self):
        """Download newer versions of the game's setup files."""
        logger.debug(f"{self.name}.update == {self.needs_update}")
        if not self.needs_update:
            return
        # Delete old files
        for file in self.old_files:
            file_path = os.path.join(self.download_path, file)
            system.rm(file_path)
        self.download_setup_files()

    def install(self, install_dir, platform):
        """Install the game.

        Extract installer files into a temporary directory and move the files
        to the destination.

        :param install_dir: Destination directory
        :param platform: The integer value associated with an OS (1, 2, or 4)
        """
        confirmation = user.confirm(f"Install {self.name}?")
        if not confirmation:
            print("Installation canceled.")
            sys.exit()

        # Check for local files first and download latest installer if either
        # outdated or nonexistent
        logger.debug(f"{self.download_files}")
        if self.download_files and self.needs_update:
            self.update_game()
        else:
            self.download_setup_files()

        try:
            installer_info = self.installers[platform]
        except KeyError:
            logger.error(f"{self.name}: No installer for platform '{platform}' found.")
            sys.exit(2)

        installer_file = os.path.basename(installer_info)
        installer = os.path.join(self.download_path, installer_file)

        # Create temp dir inside install_dir
        temp_dir = os.path.join(install_dir, "tmp/")
        system.mkdir(temp_dir)  # TODO: what to do when path already exists?

        if platform == 4:
            # Extract game files
            extract = ["unzip", installer, "-d", temp_dir, "data/noarch/*"]
            run.command(extract)

            # Move files from temp_dir to destination
            game_files = os.path.join(temp_dir, "data/noarch/")
            logger.debug(f"Moving files from {game_files} to {install_dir}")
            for file in os.listdir(game_files):
                file_path = os.path.join(game_files, file)
                system.move(file_path, install_dir)

            # Remove temp_dir
            system.rmdir(temp_dir)

        elif platform == 1:
            logger.debug(f"Installing {self.name}. Platform = {platform}")
            pass
            # TODO: use innoexctract
        elif platform == 2:
            logger.debug("macOS installer not supported")
            pass

        self.installed = True
        self.install_path = install_dir
        print(f"{self.name} installed successfully.")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"""{type(self).__name__}({self.name}, GAME INFO, {self.download_path})"""
