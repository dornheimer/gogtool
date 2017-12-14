import os


class Installer:
    """
    Contains all data related to setup files of a game or DLC.
    """
    def __init__(self, installer_data):
        self.__dict__ = installer_data
        self.file_name = os.path.basename(self.path)

    def __repr__(self):
        return self.file_name
