import unittest

from unittest.mock import patch
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=(Path('.') / '.env_test'))

from .utils import TestUtils
from app import commands
from app import common
from app.storage import local_storage

test_utils = TestUtils()


class ThawCommandTest(unittest.TestCase):

    storage: local_storage.LocalStorage

    @classmethod
    def setUpClass(cls):
        # set up local storage
        cls.storage = common.utils.GetStorage()

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
        test_utils.CreateTestFile(
            'thisisanotherfile_2', prefix=self.test_subfolder)

    @classmethod
    def tearDownClass(cls):
        # destroy local storage
        cls.storage.Destroy()

    def tearDown(self):
        # tear down the directory structure
        test_utils.DeleteFolderAndContents(self.test_folder)

    def test_thaw_requires_path(self):
        # thaw should throw an error without path
        with self.assertRaises(IceboxError):
            commands.IceboxThawCommand(None).run()

    def test_thaw_path_existence_cases(self):
        # thaw should not work if the directory is not initialized
        with self.assertRaises(IceboxError):
            commands.IceboxThawCommand(str(self.test_folder)).run()

        # thaw should throw an error if path does not exist locally and
        # does not have frozen files remotely.
        commands.IceboxInitCommand(str(self.test_folder)).run()
        path = self.test_folder / Path("doesnotexist")
        with self.assertRaises(IceboxError):
            commands.IceboxThawCommand(str(path)).run()

        # thaw should work if path does not exist locally but has frozen files
        # remotely.
        test_folder_to_be_deleted = test_utils.CreateTestFolder(
            'tobedeleted', prefix=self.test_folder)
        test_file_to_be_deleted = test_utils.CreateTestFile(
            'filetobedeleted', prefix=test_folder_to_be_deleted)
        test_file_to_be_deleted_size = test_file_to_be_deleted.stat().st_size
        commands.IceboxFreezeCommand(test_file_to_be_deleted).run()
        test_utils.DeleteFolderAndContents(test_folder_to_be_deleted)
        commands.IceboxThawCommand(str(test_folder_to_be_deleted)).run()
        self.assertTrue(test_file_to_be_deleted.exists())
        self.assertEqual(
            test_file_to_be_deleted.stat().st_size,
            test_file_to_be_deleted_size)

        # thaw should work if path exists and does not have frozen files
        commands.IceboxThawCommand(str(self.test_subfolder)).run()

        # thaw should work if path exists and has frozen files
        commands.IceboxFreezeCommand(str(self.test_subfolder)).run()
        commands.IceboxThawCommand(str(self.test_subfolder)).run()

    def test_thaw_directory(self):
        # thaw should work on an initialized directory
        # * files should have a size greater than 0 after thawing
        commands.IceboxInitCommand(str(self.test_folder)).run()
        file_size = {
            f: f.stat().st_size
            for f in self.test_folder.glob("**/*")
            if f.is_file() and f.name != ".icebox"}
        commands.IceboxFreezeCommand(str(self.test_folder)).run()
        for f in file_size.keys():
            self.assertTrue(f.exists())
            self.assertEqual(f.stat().st_size, 0)
        commands.IceboxThawCommand(str(self.test_folder)).run()
        for f, s in file_size.items():
            self.assertEqual(f.stat().st_size, s)

    def test_thaw_subdirectory(self):
        # thaw should work on a subdirectory of an initialized directory
        # * files should have a size greater than 0 after thawing
        # * files not in subfolder but inside initialize folder should be
        # unaffected
        commands.IceboxInitCommand(str(self.test_folder)).run()
        test_folder_file_size = {
            f: f.stat().st_size
            for f in self.test_folder.glob("*")
            if f.is_file() and f.name != ".icebox"}
        test_subfolder_file_size = {
            f: f.stat().st_size
            for f in self.test_subfolder.glob("*") if f.is_file()}
        commands.IceboxFreezeCommand(str(self.test_subfolder)).run()
        for f, s in test_folder_file_size.items():
            self.assertEqual(f.stat().st_size, s)
        for f in test_subfolder_file_size.keys():
            self.assertTrue(f.exists())
            self.assertEqual(f.stat().st_size, 0)
        commands.IceboxThawCommand(str(self.test_subfolder)).run()
        for f, s in test_folder_file_size.items():
            self.assertEqual(f.stat().st_size, s)
        for f, s in test_subfolder_file_size.items():
            self.assertEqual(f.stat().st_size, s)

    def test_thaw_file(self):
        # thaw should work on a single file in an initialized directory
        # * file should have a size greater than 0 after thawing
        # * other files in subfolder should be unaffected
        commands.IceboxInitCommand(str(self.test_folder)).run()
        test_subfolder_file_sizes = {
            f: f.stat().st_size
            for f in self.test_subfolder.glob("*") if f.is_file()}
        test_subfolder_file_size = self.test_subfolder_file.stat().st_size
        commands.IceboxFreezeCommand(str(self.test_subfolder_file)).run()
        commands.IceboxThawCommand(str(self.test_subfolder_file)).run()
        for f, s in test_subfolder_file_sizes.items():
            self.assertEqual(f.stat().st_size, s)

        # thawing a thawed file should not have any effect
        commands.IceboxThawCommand(str(self.test_subfolder_file)).run()
        self.assertEqual(
            self.test_subfolder_file.stat().st_size, test_subfolder_file_size)

        # thawing an overwritten frozen file should not replace contents
        # TODO: consider throwing an error to inform the user.
        with self.test_subfolder_file.open(mode='w') as f:
            f.write("overwritten data.")
        overwritten_file_size = self.test_subfolder_file.stat().st_size
        self.assertNotEqual(overwritten_file_size, test_subfolder_file_size)
        commands.IceboxThawCommand(str(self.test_subfolder_file)).run()
        self.assertEqual(
            self.test_subfolder_file.stat().st_size, overwritten_file_size)

    @patch(
        'app.commands.IceboxThawCommand._IceboxThawCommand__download_file')
    def test_thaw_download_error(self, mocked_function):
        mocked_function.side_effect = common.IceboxStorageError()
        commands.IceboxInitCommand(str(self.test_folder)).run()
        commands.IceboxFreezeCommand(str(self.test_folder_file)).run()
        # thaw should not work when an error is thrown
        commands.IceboxThawCommand(str(self.test_folder_file)).run()
        self.assertEqual(self.test_folder_file.stat().st_size, 0)
