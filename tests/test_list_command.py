import os
import unittest

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=(Path('.') / '.env_test'))

from .utils import TestUtils
from app import commands
from app import common
from app.storage import local_storage

test_utils = TestUtils()


class ListCommandTest(unittest.TestCase):

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
        self.test_subfolder_file_2 = test_utils.CreateTestFile(
            'thisisanotherfile_2', prefix=self.test_subfolder)

    @classmethod
    def tearDownClass(cls):
        # destroy local storage
        cls.storage.Destroy()

    def tearDown(self):
        # tear down the directory structure
        test_utils.DeleteFolderAndContents(self.test_folder)

    def test_list_args(self):
        # list should raise error without parent or remote arguments
        with self.assertRaises(IceboxError):
            commands.IceboxListCommand(parent=None, remote=None).run()
        with self.assertRaises(IceboxError):
            commands.IceboxListCommand(
                parent=str(self.test_folder), remote=None).run()
        with self.assertRaises(IceboxError):
            commands.IceboxListCommand(parent=None, remote='.').run()

        # list should work with remote_path argument
        commands.IceboxInitCommand(str(self.test_folder)).run()
        commands.IceboxFreezeCommand(str(self.test_folder)).run()
        commands.IceboxListCommand(
            parent=str(self.test_folder), remote='.').run()

        # list should work with recursive argument
        commands.IceboxListCommand(
            parent=str(self.test_folder), remote='.', recursive=True).run()

    def test_list_path_initialized(self):
        # list should raise error for uninitialized folder
        with self.assertRaises(IceboxError):
            commands.IceboxListCommand(
                parent=str(self.test_folder), remote='.').run()

        # list should not raise error if the path is not frozen
        commands.IceboxInitCommand(str(self.test_folder)).run()
        commands.IceboxListCommand(
            parent=str(self.test_folder), remote='.').run()

        # list should work if remote path exists
        commands.IceboxFreezeCommand(str(self.test_folder)).run()
        commands.IceboxListCommand(
            parent=str(self.test_folder), remote='.').run()
        commands.IceboxListCommand(
            parent=str(self.test_folder), remote='.', recursive=True).run()

    def test_list_output(self):
        # listing should return all frozen files in given remote path
        commands.IceboxInitCommand(str(self.test_folder)).run()
        commands.IceboxFreezeCommand(str(self.test_folder)).run()
        icebox = common.utils.FindIcebox(self.test_folder)
        # we will need to test the storage's listing here since the command
        # does not return anything but prints out
        dirs, files = ListCommandTest.storage.List(
            icebox, common.utils.GetRelativeRemotePath(
                self.test_folder, icebox.path))
        self.assertTrue(len(dirs), 1)
        self.assertEqual(dirs[0].name,  self.test_subfolder.name)
        self.assertTrue(len(files), 1)
        self.assertEqual(files[0].name, self.test_folder_file.name)

        # listing recursively should return all frozen paths relative to given
        # remote path
        dirs, files = ListCommandTest.storage.List(
            icebox, common.utils.GetRelativeRemotePath(
                self.test_folder, icebox.path), recursive=True)
        self.assertTrue(len(files), 3)
        self.assertEqual(
            files[1].name,
            self.test_subfolder.name+os.sep+self.test_subfolder_file.name)

        # thawed paths should not be removed from listed files
        commands.IceboxThawCommand(str(self.test_subfolder_file)).run()
        dirs, files = ListCommandTest.storage.List(
            icebox, common.utils.GetRelativeRemotePath(
                self.test_subfolder, icebox.path))
        self.assertTrue(len(files), 1)
        self.assertTrue(
            self.test_subfolder.name+os.sep+self.test_subfolder_file.name
            in [f.name for f in files])

        # empty directories should not be listed
        commands.IceboxThawCommand(str(self.test_subfolder_file_2)).run()
        dirs, files = ListCommandTest.storage.List(
            icebox, common.utils.GetRelativeRemotePath(
                self.test_folder, icebox.path))
        self.assertTrue(len(dirs), 0)
        self.assertFalse([f for f in files
                         if f.name.startswith(self.test_subfolder.name)])
