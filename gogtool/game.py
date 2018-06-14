import logging
import os
import re
from functools import partial

from gogtool import lgog, util

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, game_data, *, download_dir=None, install_dir=None):
        self._data = game_data
        self.name = game_data['gamename']
        self.installers = game_data['installers']
        self.linux_available = self.check_linux()
        self.server_files = self.get_server_files()
        self.downloaded_files = set()
        self.needs_update = False
        self.download_dir = download_dir
        self.install_dir = install_dir
        self.dlc_installed = False

        self.installable_dlcs = self.get_installable_dlcs()
        self.has_dlc = len(self.installable_dlcs) >= 1

    def __str__(self):
        return self.name

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}({self.name})"

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == 'download_dir' and value is not None:
            self.downloaded_files = self.find_downloaded_files()
        if name == 'downloaded_files' and value != set():
            self.needs_update = self.check_file_versions()

    @property
    def is_downloaded(self):
        return len(self.downloaded_files) > 0

    @property
    def is_installed(self):
        return self.install_dir is not None

    def check_linux(self):
        for inst in self.installers:
            if inst['platform'] == 4:
                return True
        return False

    def find_downloaded_files(self):
        installer_re = re.compile(
            r".*\.(zip|exe|bin|dmg|old|deb|tar\.gz|pkg|sh)$"
        )
        try:
            dir_content = util.listdir(self.download_dir)
        except (FileNotFoundError, TypeError):
            logger.debug("%s not downloaded", self.name)
            return set()
        else:
            return {df for df in dir_content if installer_re.search(df)}

    def get_server_files(self):
        platform = 4 if self.linux_available else 1
        files = set()
        for inst in self.installers:
            if inst['platform'] != platform:
                continue
            file_path = inst['path']
            files.add(file_path)
        return files

    def check_file_versions(self):
        current, old = self.match_server_files()
        return len(current) == 0

    def get_installable_dlcs(self):
        dlcs = []
        if 'dlcs' not in self._data:
            return dlcs
        for dlc_data in self._data['dlcs']:
            if 'installers' not in dlc_data:
                continue
            dlc_name = dlc_data['gamename']
            dlc_download_dir = None
            if self.download_dir:
                dlc_download_dir = os.path.join(self.download_dir, 'dlc', dlc_name)
            dlc = DLC(self, dlc_data, download_dir=dlc_download_dir)
            dlcs.append(dlc)
        return dlcs

    def match_server_files(self):
        downloaded_file_names = {
            os.path.basename(fp) for fp in self.downloaded_files
            }
        server_file_names = {os.path.basename(fp) for fp in self.server_files}
        matched = downloaded_file_names & server_file_names
        unmatched = downloaded_file_names - server_file_names
        return (matched, unmatched)

    def match_downloaded(self, basename=False):
        server_files = self.server_files
        if basename:
            server_files = [os.path.basename(sf) for sf in self.server_files]
        if not self.is_downloaded:
            # Return all available files on the server
            return [sf for sf in server_files]

        # Return only files that match downloaded files (by extension)
        ext_re = re.compile(r"\..+")
        return_match = lambda string: ext_re.search(string).group(0)
        downloaded_ext = {return_match(df) for df in self.downloaded_files}
        return [sf for sf in server_files if return_match(sf) in downloaded_ext]

    def download(self, download_dir):
        platform = 'l' if self.linux_available else 'w'
        if self.is_downloaded and not self.needs_update:
            print("Game files are up-to-date.")
            return
        elif self.is_downloaded and self.needs_update:
            delete_old = util.user_confirm("Delete old setup files?")
            if delete_old:
                self.delete_setup_files()

        lgog.download(self.name, dest=download_dir, platform=platform)

        # Update downloaded files
        self.download_dir = os.path.join(download_dir, self.name)
        self.downloaded_files = self.find_downloaded_files()
        self.needs_update = self.check_file_versions()

    def install(self, install_dir, download_dir):
        if not self.linux_available:
            print("Linux version not available. WINE support not implemented.")
            return
        if self.is_installed and not self.needs_update:
            print(f"Latest version of '{self.name}' is already installed.")
            return
        elif self.is_installed and self.needs_update:
            user_prompt = f"Installation of '{self.name}' is outdated. Update?"
            update = util.user_confirm(user_prompt)
            if update:
                self.download(download_dir)
                self.install(install_dir)
            else:
                return
        elif not self.is_downloaded:
            self.download(download_dir)

        installer = os.path.basename(self.server_files.pop())
        installer_path = os.path.join(self.download_dir, installer)
        self.install_dir = os.path.join(install_dir, self.name)
        util.extract_linux_installer(installer_path, self.install_dir)

        if self.has_dlc:
            self.install_dlc()

    def install_dlc(self):
        for dlc in self.installable_dlcs:
            if not dlc.is_downloaded:
                continue
            installer_path = os.path.join(dlc.download_dir, dlc.server_files)
            util.extract_linux_installer(installer_path, self.install_dir)
        self.dlc_installed = True

    def update(self):
        logger.warning("Update not implemented")
        print("Update not implemented")

    def uninstall(self):
        if not self.is_installed:
            log_msg = f"'{self.name}' is not installed."
            logger.error(log_msg)
            print(log_msg)
            return
        try:
            # Only delete files and directories in the file list
            self.uninstall_from_list()
        except FileNotFoundError:
            logger.warning("File list not found")
            user_prompt = "No list of installed files found. Remove entire game folder?"
            if util.user_confirm(user_prompt):
                util.rmdir(self.install_dir)

        if util.user_confirm("Delete setup files?"):
            self.delete_setup_files()

    def uninstall_from_list(self):
        logger.debug("Reading file list")
        file_list = os.path.join(self.install_dir, 'files.txt')
        with open(file_list) as f:
            fformat = partial(Game.format_file_path, self.install_dir)
            installed_files = {fformat(fp) for fp in f.readlines()}

        dir_content = util.listdir(self.install_dir)
        for item in dir_content:
            if item not in installed_files:
                continue
            if os.path.isfile(item):
                util.rm(item)
            elif os.path.isdir(item):
                util.rmdir(item)
        util.rm(file_list)

        dir_content = util.listdir(self.install_dir)
        if not dir_content:
            util.rmdir(self.install_dir)

    def delete_setup_files(self):
        if not self.is_downloaded:
            log_msg = f"No downloaded files for '{self.name}' found."
            logger.error(log_msg)
            print(log_msg)
            return
        util.rm_all(self.downloaded_files)
        # Update downloaded files
        self.downloaded_files = self.find_downloaded_files()

    def remove(self):
        if self.is_installed:
            self.uninstall()
        if self.is_downloaded:
            self.delete_setup_files()

    def view_install_dir(self):
        if not self.is_installed:
            log_msg = f"'{self.name}' is not installed."
            logger.error(log_msg)
            print(log_msg)
            return
        util.open_dir(self.install_dir)

    def run(self):
        if not self.is_installed:
            log_msg = f"'{self.name}' is not installed."
            logger.error(log_msg)
            print(log_msg)
            return
        if self.linux_available:
            start_script = os.path.join(self.install_dir, 'start.sh')
            util.run_command([start_script], silent=True)

    @staticmethod
    def format_file_path(game_install_dir, filename):
        file_ = filename.strip().replace('data/noarch/', '')
        file_path = os.path.join(game_install_dir, file_)
        return os.path.normpath(file_path)


class DLC(Game):
    def __init__(self, base_game, dlc_data, download_dir):
        super().__init__(dlc_data, download_dir=download_dir)
        self.base_game = base_game

        if self.base_game.is_installed:
            self.install_dir = base_game.install_dir

    @property
    def is_installed(self):
        return self.base_game.dlc_installed


class Patch(DLC):
    pass
