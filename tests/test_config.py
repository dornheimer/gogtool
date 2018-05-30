import os
import unittest

import yaml

from gogtool import config
from gogtool.config import DEFAULT_CONFIG

DIR_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIG_DICT = {
    'install_dir': "test_config/install_dir",
    'download_dir': "test_config/download_dir",
    'lgog_config_path': os.path.join(
        DIR_PATH,
        "test_config/lgog_testconfig.cfg"
    ),
    'lgog_data_path': "test/gamedetails.json"
    }
CONFIG_FILE_PATH = os.path.join(DIR_PATH, "test_config/valid_config.yaml")


def write_test_config():
    with open(CONFIG_FILE_PATH, 'w') as f:
        f.write(yaml.dump(CONFIG_DICT))


class TestConfig(unittest.TestCase):

    write_test_config()

    def test_convert_bool(self):
        self.assertFalse(config.convert_bool('false'))
        self.assertTrue(config.convert_bool('true'))
        self.assertEqual('string', config.convert_bool('string'))

    def test_load_user_config_default(self):
        user_config = config.load_user_config()
        self.assertEqual(user_config, {})

    def test_load_user_config_from_file(self):
        user_config = config.load_user_config(CONFIG_FILE_PATH)
        self.assertDictEqual(user_config, CONFIG_DICT)

    def test_load_user_config_from_env(self):
        os.environ['GOGTOOL_CONFIG'] = CONFIG_FILE_PATH
        user_config = config.load_user_config()
        self.assertDictEqual(user_config, CONFIG_DICT)

    def test_load_lgog_config(self):
        lgog_config_path = os.path.join(DIR_PATH, CONFIG_DICT['lgog_config_path'])
        expected_lgog_config = {
            'exclude': 'extras',
            'include': 'installers,covers,dlcs',
            'insecure': False,
            'directory': 'test/directory'
        }
        lgog_config = config.load_lgog_config(lgog_config_path)
        self.assertDictEqual(lgog_config, expected_lgog_config)

    def test_configure_gogtool_default(self):
        gogtool_config = config.configure_gogtool()
        lgog_config = config.load_lgog_config(
            DEFAULT_CONFIG['lgog_config_path']
        )
        self.assertEqual(
            gogtool_config['install_dir'],
            DEFAULT_CONFIG['install_dir']
        )
        self.assertEqual(
            gogtool_config['download_dir'], lgog_config['directory']
        )

    def test_configure_gogtool_user_config(self):
        gogtool_config = config.configure_gogtool(CONFIG_FILE_PATH)
        self.assertEqual(
            gogtool_config['install_dir'],
            CONFIG_DICT['install_dir']
        )
        self.assertEqual(
            gogtool_config['download_dir'],
            CONFIG_DICT['download_dir']
        )


if __name__ == '__main__':
    unittest.main()
