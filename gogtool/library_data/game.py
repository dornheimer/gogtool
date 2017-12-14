from .installer import Installer
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
            Creates Installer objects
        """
        try:
            installer_data = self.game_data["installers"]
        except KeyError:
            logger.warning(f"no setup files for {self.gamename} found")
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
