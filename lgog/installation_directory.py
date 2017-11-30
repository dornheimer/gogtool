from lgog.helper.directory import Directory
from lgog.helper.log import logger


class InstallationDir(Directory):
    def __init__(self, path):
        super().__init__(path)
