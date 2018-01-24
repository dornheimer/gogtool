import os
import unittest

from testfixtures import LogCapture

from gogtool.directory import Directory


VALID_PATH = os.path.dirname(__file__)
INVALID_PATH = "directory/does/not/exist"


class TestLogging(unittest.TestCase):

    def setUp(self):
        self.capture = LogCapture()

    def tearDown(self):
        self.capture.uninstall()

    def test_init_invalid(self):
        with self.assertRaises(SystemExit) as cm:
            directory = Directory(INVALID_PATH)
            self.assertEqual(directory.path, None)

        self.assertTrue(cm.exception.code, 2)
        self.capture.check(
            ('gogtool.helper.log',
             'ERROR',
             f"Directory could not be initialized: '{INVALID_PATH}' does not exist.")
        )

    def test_init_valid(self):
        directory = Directory(VALID_PATH)
        self.assertEqual(directory.path, VALID_PATH)

        self.capture.check(
            ('gogtool.helper.log',
             'DEBUG',
             f"Directory initialized with {VALID_PATH}")
        )


if __name__ == '__main__':
    unittest.main()
