import unittest

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=(Path('.') / '.env_test'))

from .utils import TestUtils
from app import commands
from app import common
from app import config
from app.elements.icebox import IceboxError
from app.storage import local_storage

test_utils = TestUtils()


class InitCommandTest(unittest.TestCase):

    test_folder: Path
    test_folder_file: Path
    test_subfolder: Path
    storage: local_storage.LocalStorage

    @classmethod
    def setUpClass(cls):
        cls.test_folder = test_utils.CreateTestFolder(
            'init_test')
        cls.test_subfolder = test_utils.CreateTestFolder(
            'subfolder', prefix=cls.test_folder)
        cls.test_folder_file = test_utils.CreateTestFile(
            'thisisafile', prefix=cls.test_folder)
        cls.storage = common.utils.GetStorage()

    @classmethod
    def tearDownClass(cls):
        test_utils.DeleteFolderAndContents(cls.test_folder)
        cls.storage.Destroy()

    def test_init_folder_needs_path(self):
        """Init command requires a valid existing directory to run."""
        # init without path or on non-existent folder should throw error
        with self.assertRaises(IceboxError):
            commands.IceboxInitCommand(None).run()
        with self.assertRaises(IceboxError):
            commands.IceboxInitCommand("doesnotexist").run()

        # init should not work on a path that is not a directory
        with self.assertRaises(IceboxError):
            commands.IceboxInitCommand(
                str(InitCommandTest.test_folder_file)).run()

    def test_init_folder_checks_parents(self):
        """Init command cannot be run in a subfolder of an initialized
        directory."""
        # init should work if no parent folder is initialized
        commands.IceboxInitCommand(str(InitCommandTest.test_folder)).run()
        icebox_path = (
            InitCommandTest.test_folder / Path(config.ICEBOX_FILE_NAME))
        self.assertTrue(icebox_path.exists())
        self.assertTrue(icebox_path.is_file())

        # init should not initialize a folder that is already initialized
        with self.assertRaises(IceboxError):
            commands.IceboxInitCommand(
                str(InitCommandTest.test_folder)).run()

        # init should not work if a parent folder is initialized
        with self.assertRaises(IceboxError):
            commands.IceboxInitCommand(
                str(InitCommandTest.test_subfolder)).run()
