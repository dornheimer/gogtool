from datetime import datetime
import json
import os

from gogtool.helper.directory import Directory
from gogtool.helper.log import logger


class GameData:
    """
    Parsed data from JSON dictionary with methods to recognize setup files.
    """
    def __init__(self, game_data):
        self.game_data = game_data

        self.gamename = None
        self.title = None
        self.setup_files = {}
        self.dlcs = {}
        self.is_bonus_content = False

        self._parse_game_data()

    def __repr__(self):
        return self.gamename

    def _parse_game_data(self):
        self.gamename = self.game_data["gamename"]
        self.title = self.game_data["title"]
        self._initialize_setup_files()
        self._initialize_dlcs()

    def _initialize_setup_files(self):
        """Look for setup files group them by platform.

        Note:
            Creates InstallerData objects
        """
        try:
            installer_data = self.game_data["installers"]
        except KeyError:
            logger.warning(f"no setup files for {self.gamename} found")
            self.is_bonus_content = True
        else:
            for inst in installer_data:
                self.setup_files.setdefault(
                    inst["platform"], []).append(InstallerData(inst))

    def _initialize_dlcs(self):
        """Look for DLC and add it if it exists.

        Note:
            Creates DLCData objects
        """
        try:
            dlc_data = self.game_data["dlcs"]
            logger.debug(f"DLC for {self.gamename} found")
        except KeyError:
            pass
        else:
            for dlc in dlc_data:
                self.dlcs[dlc["gamename"]] = DLCData(dlc)


class DLCData(GameData):
    """
    Parsed data from JSON dictionary, inherits from GameData.
    """
    def __init__(self, game_data):
            self.game_data = game_data

            self.gamename = None
            self.setup_files = {}

            self._parse_game_data()

    def _parse_game_data(self):
        self.gamename = self.game_data["gamename"]
        self._initialize_setup_files()


class InstallerData:
    """
    Contains all data related to setup files of a game or DLC.
    """
    def __init__(self, installer_data):
        self.__dict__ = installer_data
        self.file_name = os.path.basename(self.path)

    def __repr__(self):
        return self.file_name


class LibraryData(Directory):
    """
    Library data imported from lgogdownloader's gamedetails.json.
    """
    def __init__(self, path):
        super().__init__(path)
        self.library_data = {}

        self.date = None
        self.games = {}

        self._get_library_data()
        self._initialize_library()

    def _get_library_data(self):
        """Convert gamedetails.json file into a python dictionary."""
        with open(self.path) as data:
            library_data = json.load(data)

        self.library_data = library_data
        logger.debug(f"imported data from {os.path.basename(self.path)}")

    def _initialize_library(self):
        self.date = self.library_data["date"]

        for game_data in self.library_data["games"]:
            self.games[game_data["gamename"]] = GameData(game_data)

    @property
    def games_list(self):
        return list(self.games)

    @property
    def game_titles(self):
        return [g.title for g in self.games.values()]

    @property
    def size(self):
        return len(self.games)

    @property
    def is_outdated(self):
        """Check if game details file is older than two days."""
        logger.info("Checking games data creation date...")
        creation_date = datetime.strptime(self.date, "%Y%m%dT%H%M%S")
        days_since_last_update = (datetime.now() - creation_date).days
        outdated = days_since_last_update >= 2

        str_outdated = "needs update" if outdated else "ok"
        logger.debug("gamedetails.json created on: {}, age: {} days ({})".format(
                     creation_date.strftime('%Y%m%d'), days_since_last_update, str_outdated))

        return outdated

    def get_game_data(self, game_name):
        """Get data associated with game from the library data.

        :param game_name: Game name as stored in DownloadDir.
        :return: Dictionary entry for game_name.
        """
        try:
            return self.games[game_name]
        except KeyError:
            logger.warning(f"Game info for {game_name} not found")
            return None
