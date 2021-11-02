import unittest

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=(Path('.') / '.env_test'))

from .utils import TestUtils
from .utils import TEST_FOLDER
from app import commands
from app import common
from app import config
from app.elements.icebox import IceboxError
from app.storage import local_storage

test_utils = TestUtils()


class CloneCommandTest(unittest.TestCase):

    storage: local_storage.LocalStorage

    @classmethod
    def setUpClass(cls):
        cls.storage = common.utils.GetStorage()

    def setUp(self):
        # set up the directory structure
        self.base_folder = test_utils.CreateTestFolder(
            'clone_test_base')
        self.file_frozen = test_utils.CreateTestFile(
            'frozen', prefix=self.base_folder)
        self.file_not_frozen = test_utils.CreateTestFile(
            'notfrozen', prefix=self.base_folder)
        self.icebox = commands.IceboxInitCommand(str(self.base_folder)).run()
        commands.IceboxFreezeCommand(str(self.file_frozen)).run()
        self.clone_path = Path(TEST_FOLDER) / Path("clone_test_cloned")

    @classmethod
    def tearDownClass(cls):
        cls.storage.Destroy()

    def tearDown(self):
        # tear down the directory structure
        test_utils.DeleteFolderAndContents(self.base_folder)
        if self.clone_path.exists():
            test_utils.DeleteFolderAndContents(self.clone_path)

    def test_clone_needs_icebox_and_empty_path(self):
        """Clone command requires a valid icebox and an empty path to run."""
        # clone without valid icebox or empty path should raise error
        with self.assertRaises(IceboxError):
            commands.IceboxCloneCommand(None, None).run()

        # clone with an existing folder should raise error
        existing_path = test_utils.CreateTestFolder(
            'clone_test_existing')
        with self.assertRaises(IceboxError):
            commands.IceboxCloneCommand(self.icebox.id, str(existing_path)).run()

        # cloning a non-existent icebox should raise error
        with self.assertRaises(IceboxError):
            commands.IceboxCloneCommand("doesnotexist", str(self.clone_path)).run()

    def test_clone_folder_checks_parents(self):
        """Clone command cannot be run in the tree of an existing icebox."""
        # clone should work if no parent folder is an icebox
        commands.IceboxCloneCommand(self.icebox.id, str(self.clone_path)).run()
        icebox_path = (
            self.clone_path / Path(config.ICEBOX_FILE_NAME))
        self.assertTrue(icebox_path.exists())
        self.assertTrue(icebox_path.is_file())

        # check hierarchy
        cloned_frozen = self.clone_path / Path("frozen")
        cloned_not_frozen = self.clone_path / Path("notfrozen")
        self.assertTrue(cloned_frozen.exists())
        self.assertTrue(cloned_frozen.is_file())
        self.assertFalse(cloned_not_frozen.exists())

        # clone should not work if the folder is already an icebox
        with self.assertRaises(IceboxError):
            commands.IceboxCloneCommand(
                self.icebox.id, str(self.clone_path)).run()

        # clone should not work if a parent folder is an icebox
        clone_subfolder = self.clone_path / Path("subfolder")
        with self.assertRaises(IceboxError):
            commands.IceboxCloneCommand(
                self.icebox.id, str(clone_subfolder)).run()
