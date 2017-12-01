from lgog.helper.directory import Directory
from lgog.helper.log import logger


class InstallDir(Directory):
    """
    Store information about installed GOG games.
    """
    def __init__(self, path):
        super().__init__(path)
        self.installed_games = []

    # keep track of installed games
    # install/update (extract) downloaded installers here
    # manage save games??
    # connect to lutris??
