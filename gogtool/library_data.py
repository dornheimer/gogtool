from datetime import datetime
import json
import os

from .directory import Directory
from gogtool.helper.log import logger


class LibraryData(Directory):
    """
    Library data imported from lgogdownloader's gamedetails.json.
    """
    def __init__(self, path):
        super().__init__(path)
        self._games = {}
        self._library_data = {}

        self._import_library_data()
        self._initialize_library()

    def __len__(self):
        return len(self._games)

    def __iter__(self):
        return iter(self._games.values())

    def _import_library_data(self):
        """Convert gamedetails.json file into a python dictionary."""
        with open(self.path) as data:
            library_data = json.load(data)

        self._library_data = library_data
        logger.debug(f"imported data from {os.path.basename(self.path)}")

    def _initialize_library(self):
        """Map game_name to GameData object.

        Note:
            Created GameData objects.
        """
        for game_data in self._library_data["games"]:
            game_name = game_data["gamename"]
            self._games[game_name] = GameData(game_data)

    @property
    def game_titles(self):
        return [game.title for game in self]

    @property
    def is_outdated(self):
        """Check if game details file is older than two days.

        :return: True if game is outdated.
        """
        logger.info("Checking games data creation date...")
        date = self._library_data["date"]
        creation_date = datetime.strptime(date, "%Y%m%dT%H%M%S")
        days_since_last_update = (datetime.now() - creation_date).days
        outdated = days_since_last_update >= 2

        str_outdated = "needs update" if outdated else "ok"
        logger.debug("gamedetails.json created on: {}, age: {} days ({})".format(
                     creation_date.strftime('%Y%m%d'), days_since_last_update, str_outdated))

        return outdated


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
            Creates Installer objects
        """
        try:
            installer_data = self.game_data["installers"]
        except KeyError:
            logger.info(f"no setup files for {self.gamename} found")
            self.is_bonus_content = True
        else:
            for inst in installer_data:
                self.setup_files.setdefault(
                    inst["platform"], []).append(Installer(inst))

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


class Installer:
    """
    Contains all data related to setup files of a game or DLC.
    """
    def __init__(self, installer_data):
        self.__dict__ = installer_data
        self.file_name = os.path.basename(self.path)

    def __repr__(self):
        return self.file_name
