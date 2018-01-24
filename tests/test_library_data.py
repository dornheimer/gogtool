import os
import unittest

from gogtool.library_data import LibraryData, GameData, DLCData, Installer


DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(DIR, "test_library_data/gamedetails.json")

GAME_INFO = {
    "gamename": "age_of_wonders",
    "title": "Age of Wonders",
    "installers": [
        {
         "gamename": "age_of_wonders",
         "id": "en1installer0",
         "path": "/age_of_wonders/pc/setup_age_of_wonders_2.0.0.13.exe",
         "platform": 1,
        }
    ]
}

GAME_INFO_DLC = {
    "gamename": "darkest_dungeon",
    "title": "Darkest Dungeon",
    "dlcs": [
        {
         "gamename": "dd_the_crimson_court",
         "title": "DLC: DD: The Crimson Court",
         "installers": [
            {
             "gamename": "dd_the_crimson_court",
             "id": "en1installer0",
             "path": "/6748/setup_dd_the_crimson_court_21142_(16136).exe",
             "platform": 1,
            },
         ],
        }
    ],
    "installers": [
        {
         "gamename": "darkest_dungeon",
         "id": "en1installer0",
         "path": "/6748/setup_darkest_dungeon_21142_(16136).exe",
         "platform": 1,
        }
    ],
}

INSTALLER_INFO = {
     "gamename": "age_of_wonders",
     "id": "en1installer0",
     "path": "/age_of_wonders/pc/setup_age_of_wonders_2.0.0.13.exe",
     "platform": 1,
}

DLC_INFO = {
    "gamename": "dd_the_crimson_court",
    "title": "DLC: Darkest Dungeon: The Crimson Court",
    "installers": [
        {
         "gamename": "dd_the_crimson_court",
         "id": "en1installer0",
         "path": "/6748/setup_dd_the_crimson_court_21142_(16136).exe",
         "platform": 1,
        }
    ]
}


LIBRARY = LibraryData(DATA_PATH)
GAME = GameData(GAME_INFO)
GAME_DLC = GameData(GAME_INFO_DLC)
INSTALLER = Installer(INSTALLER_INFO)
DLC = DLCData(DLC_INFO)


class TestLibraryData(unittest.TestCase):

    def test_num_games(self):
        self.assertEqual(len(LIBRARY), 158)

    def test_game_titles(self):
        self.assertEqual(LIBRARY.game_titles[0], 'Age of Wonders')
        self.assertEqual(len(LIBRARY), len(LIBRARY.game_titles))

    def test_outdated(self):
        self.assertTrue(LIBRARY.is_outdated)

    def test_single_game(self):
        game = LIBRARY._games["age_of_wonders"]
        self.assertIsInstance(game, GameData)
        self.assertFalse(game.is_bonus_content)


class TestGameData(unittest.TestCase):

    def test_init(self):
        self.assertEqual(GAME.game_data, GAME_INFO)
        self.assertEqual(GAME.gamename, "age_of_wonders")
        self.assertEqual(GAME.title, 'Age of Wonders')
        self.assertEqual(GAME.dlcs, {})
        self.assertFalse(GAME.is_bonus_content)

    def test_initialize_setup_files(self):
        installer = GAME.setup_files[1][0]
        self.assertIsInstance(installer, Installer)
        self.assertEqual(installer.file_name,
                         "setup_age_of_wonders_2.0.0.13.exe")

    def test_initialize_setup_files_dlc(self):
        self.assertIn('dd_the_crimson_court', GAME_DLC.dlcs)
        dlc = GAME_DLC.dlcs["dd_the_crimson_court"]
        self.assertIsInstance(dlc, DLCData)


class TestDLCData(unittest.TestCase):

    def test_init(self):
        self.assertEqual(DLC.game_data, DLC_INFO)
        self.assertEqual(DLC.gamename, "dd_the_crimson_court")

    def test_initialize_setup_files(self):
        dlc_installer = DLC.setup_files[1][0]
        self.assertIsInstance(dlc_installer, Installer)
        self.assertEqual(dlc_installer.file_name,
                         "setup_dd_the_crimson_court_21142_(16136).exe")


class TestInstaller(unittest.TestCase):

    def test_init(self):
        self.assertEqual(INSTALLER.file_name,
                         "setup_age_of_wonders_2.0.0.13.exe")


if __name__ == '__main__':
    unittest.main()
