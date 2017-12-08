import os
import sys

import lgog.helper.lgogdownloader as lgogdownloader
from lgog.helper import user
from lgog.helper import run
from lgog.helper import system
from lgog.helper.log import logger


class Game:
    """
    Data and methods related to a single game in the library.
    """
    def __init__(self, name, game_info, download_path, download_files):
        self.name = name
        self.game_info = game_info

        self.downloaded = False
        self.download_path = download_path
        self.download_files = download_files

        self.installed = False
        self.install_path = None

        self.setup_files = {}
        self.installers = {}
        self.dlc = {}

        self.needs_update = False
        self.download = False

        self.conf = False
        self.old_files = []

        self._get_setup_files()
        self._get_dlc()

    @property
    def platform(self):
        """Set platform to linux if available.

        Note:
            4=linux, 1=windows
        """
        return 4 if 4 in self.setup_files else 1

    # def _extract_from_game_info(self, key, dlc=False):
    #     """Get item from game_info dictionary.
    #
    #     :param key: dictionary key of the item.
    #     :param dlc: look in dlc data for game
    #     """
    #     values = {}
    #     try:
    #         for v in self.game_info[key]:
    #             values.setdefault(v['platform'], []).append(v['path'])
    #
    #         return values
    #
    #     except KeyError:
    #         logger.debug(f"No {key} for {self.name} found")
    #         return None

    def _get_installers(self, data=None, dlc=False, id_prefix='en'):
        """
        Get setup files from game info.

        :param dlc: look in dlc data for game
        :param id_prefix: language identifier string (default='en')
        """
        platforms = {4, 1}
        installers = {}

        if data is None:
            data = self.game_info

        try:
            if dlc:
                data = self.game_info["dlcs"]
                for el in data:
                    if "installers" in el:
                        logger.debug(f"dlc: {el['gamename']} for {self.name} found")
                        installers = self._get_installers(el)
            else:
                for i in data["installers"]:
                    if i['platform'] in platforms and i['id'].startswith(id_prefix):
                        installers.setdefault(i['platform'], []).append(i['path'])
                        installers["game_name"] = i["gamename"]
        except KeyError:
            if not dlc:
                logger.debug(f"No installer for {self.name} found")
            return None
        else:
            return installers

    def _get_setup_files(self):
        self.setup_files = self._get_installers()

        # Some games have multiple setup files and only one executable installer
        for platform, files in self.setup_files.items():
            for file_name in files:
                if file_name.endswith((".exe", ".sh", ".dmg")):
                    self.installers[platform] = file_name
                    break

    def _get_dlc(self):
        self.dlc = self._get_installers(dlc=True)

    def check_for_update(self):
        """Compare local file versions to those on the server.

        Result is stored in self.update.

        :return: True or False
        """
        server_path = self.setup_files[self.platform]
        server_files = [os.path.basename(sp) for sp in server_path]

        same_files = all([(sf in self.download_files) for sf in server_files])
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
        if self.download_files != [] and self.needs_update:
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
