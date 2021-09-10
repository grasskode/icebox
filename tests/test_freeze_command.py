import unittest

from unittest.mock import patch
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=(Path('.') / '.env_test'))

from .utils import TestUtils
from app import commands
from app import common
from app.elements.icebox import IceboxError
from app.storage import local_storage
from app.storage.icebox_storage import IceboxStorageError

test_utils = TestUtils()


class FreezeCommandTest(unittest.TestCase):

    storage: local_storage.LocalStorage

    @classmethod
    def setUpClass(cls):
        # set up local storage
        cls.storage = common.utils.GetStorage()

    @classmethod
    def tearDownClass(cls):
        # destroy local storage
        cls.storage.Destroy()

    def setUp(self):
        # set up the directory structure
        self.test_folder = test_utils.CreateTestFolder(
            'init_test')
        self.test_subfolder = test_utils.CreateTestFolder(
            'subfolder', prefix=self.test_folder)
        self.test_folder_file = test_utils.CreateTestFile(
            'thisisafile', prefix=self.test_folder)
        self.test_subfolder_file = test_utils.CreateTestFile(
            'thisisanotherfile', prefix=self.test_subfolder)

    def tearDown(self):
        # tear down the directory structure
        test_utils.DeleteFolderAndContents(self.test_folder)

    def test_freeze_requires_path(self):
        # freeze should throw an error without path or if path is non existent
        with self.assertRaises(IceboxError):
            commands.IceboxFreezeCommand(None).run()
        with self.assertRaises(IceboxError):
            commands.IceboxFreezeCommand("doesnotexist").run()

    def test_freeze_directory(self):
        # freeze should not work if the directory is not initialized
        with self.assertRaises(IceboxError):
            commands.IceboxFreezeCommand(str(self.test_folder)).run()

        # freeze should work on an initialized directory
        # * files should have a size of 0 after freezing
        commands.IceboxInitCommand(str(self.test_folder)).run()
        files = [
            f for f in self.test_folder.glob("**/*")
            if f.is_file() and f.name != ".icebox"]
        commands.IceboxFreezeCommand(str(self.test_folder)).run()
        for f in files:
            print(f"{f} -> {f.stat().st_size}")
            self.assertTrue(f.exists())
            self.assertEqual(f.stat().st_size, 0)

    def test_freeze_subdirectory(self):
        # freeze should work on a subdirectory of an initialized directory
        # * files should have a size of 0 after freezing
        # * files not in subfolder but inside initialize folder should be
        # unaffected
        commands.IceboxInitCommand(str(self.test_folder)).run()
        files = [f for f in self.test_subfolder.glob("**/*") if f.is_file()]
        test_folder_file_size = self.test_folder_file.stat().st_size
        commands.IceboxFreezeCommand(str(self.test_subfolder)).run()
        for f in files:
            self.assertTrue(f.exists())
            self.assertEqual(f.stat().st_size, 0)
        self.assertTrue(self.test_folder_file.exists())
        self.assertEqual(
            self.test_folder_file.stat().st_size, test_folder_file_size)

    def test_freeze_file(self):
        # freeze should work on a single file in an initialized directory
        # * file should have a size of 0 after freezing
        # * other files in subfolder should be unaffected
        file_size = {
            f: f.stat().st_size
            for f in self.test_subfolder.glob("**/*") if f.is_file()}
        commands.IceboxInitCommand(str(self.test_folder)).run()
        commands.IceboxFreezeCommand(str(self.test_subfolder_file)).run()
        for f, s in file_size.items():
            self.assertTrue(f.exists())
            if f == self.test_subfolder_file:
                self.assertEqual(f.stat().st_size, 0)
            else:
                self.assertEqual(f.stat().st_size, s)

        # freezing a frozen file should not have any effect
        commands.IceboxFreezeCommand(str(self.test_subfolder_file)).run()
        self.assertTrue(self.test_subfolder_file.exists())
        self.assertEqual(self.test_subfolder_file.stat().st_size, 0)

        # freezing an overwritten file should freeze again
        with self.test_subfolder_file.open(mode='w') as f:
            f.write("overwritten data.")
        self.assertGreater(self.test_subfolder_file.stat().st_size, 0)
        commands.IceboxFreezeCommand(str(self.test_subfolder_file)).run()
        self.assertTrue(self.test_subfolder_file.exists())
        self.assertEqual(self.test_subfolder_file.stat().st_size, 0)

    @patch(
        'app.commands.IceboxFreezeCommand._IceboxFreezeCommand__upload_file')
    def test_freeze_upload_error(self, mocked_function):
        mocked_function.side_effect = IceboxStorageError()
        # freeze should not work when an error is thrown
        commands.IceboxInitCommand(str(self.test_folder)).run()
        commands.IceboxFreezeCommand(str(self.test_folder_file)).run()
        self.assertGreater(self.test_folder_file.stat().st_size, 0)
