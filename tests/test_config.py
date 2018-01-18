import os
import unittest

from gogtool.helper.config import parse_config

dir_path = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(dir_path, "test_config/valid_config.cfg")

expected_output = {
    'verbose': False,
    'directory': '/home/iiu/Downloads/lgogdownloader/',
    'limit-rate': 0,
    'platform': 'l'
}


class TestUserInput(unittest.TestCase):

    def test_parse_config(self):
        self.assertEqual(parse_config(CONFIG_FILE), expected_output)
        self.assertEqual(parse_config(CONFIG_FILE, 'directory'),
                         expected_output['directory'])
        self.assertEqual(parse_config(CONFIG_FILE, 'limit-rate'),
                         expected_output['limit-rate'])
        self.assertEqual(parse_config(CONFIG_FILE, 'verbose'),
                         expected_output['verbose'])


if __name__ == '__main__':
    unittest.main()
