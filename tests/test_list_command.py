import shutil
import unittest

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=(Path('.') / '.env_test'))

from .utils import TestUtils
from app import common
from app import commands
from app.commands.list import ListResult
from app.elements.icebox import IceboxError
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
        ## remote
        self.test_folder_1 = test_utils.CreateTestFolder(
            'folder_1')
        self.test_subfolder_1 = test_utils.CreateTestFolder(
            'subfolder_1', prefix=self.test_folder_1)
        self.test_subfile_1 = test_utils.CreateTestFile(
            'file1', prefix=self.test_subfolder_1)
        self.test_folder_2 = test_utils.CreateTestFolder(
            'folder_2')
        self.test_folder_3 = test_utils.CreateTestFolder(
            'folder_3')
        ## local
        self.test_folder = test_utils.CreateTestFolder(
            'init_test')
        self.test_folder_file = test_utils.CreateTestFile(
            'thisisafile', prefix=self.test_folder)
        self.test_subfolder = test_utils.CreateTestFolder(
            'subfolder', prefix=self.test_folder)
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
        test_utils.DeleteFolderAndContents(self.test_folder_1)
        test_utils.DeleteFolderAndContents(self.test_folder_2)
        test_utils.DeleteFolderAndContents(self.test_folder_3)
        test_utils.DeleteFolderAndContents(self.test_folder)

    def test_list_remote(self):
        # clean init
        ListCommandTest.storage.Destroy()
        
        # list_all should not return any iceboxes when there are none
        # initialized
        res: ListResult = commands.IceboxListCommand().list_remote(None)
        self.assertTrue(res.is_remote)
        self.assertEqual(len(res.folders), 0)
        self.assertEqual(len(res.files), 0)

        # any initialized icebox should immediately reflect in list_all
        commands.IceboxInitCommand(str(self.test_folder_1)).run()
        res: ListResult = commands.IceboxListCommand().list_remote(None)
        icebox_1 = common.utils.FindIcebox(self.test_folder_1)
        self.assertEqual(len(res.folders), 1)
        self.assertTrue(res.folders[0].name.startswith(icebox_1.id))
        
        # listing should return the correct number of files and folders
        commands.IceboxInitCommand(str(self.test_folder_2)).run()
        commands.IceboxInitCommand(str(self.test_folder_3)).run()
        res: ListResult = commands.IceboxListCommand().list_remote(None)
        self.assertEqual(len(res.folders), 3)
        
        # listing should work with a path
        commands.IceboxFreezeCommand(str(self.test_folder_1)).run()
        res: ListResult = commands.IceboxListCommand().list_remote(icebox_1.id)
        self.assertEqual(len(res.folders), 1)
        self.assertEqual(len(res.files), 0)
        res: ListResult = commands.IceboxListCommand().list_remote(f"{icebox_1.id}/subfolder_1")
        self.assertEqual(len(res.folders), 0)
        self.assertEqual(len(res.files), 1)
        
        # list_all should show an icebox even if it is deleted locally
        shutil.rmtree(self.test_folder_1)
        self.assertFalse(self.test_folder_1.exists())
        res: ListResult = commands.IceboxListCommand().list_remote(None)
        self.assertEqual(len(res.folders), 3)
        self.assertIn(f"{icebox_1.id}", [x.name for x in res.folders])

    def test_local(self):
        # clean init
        ListCommandTest.storage.Destroy()

        # list should raise error for uninitialized folder
        with self.assertRaises(IceboxError):
            commands.IceboxListCommand().list_local(str(self.test_folder))

        # list should not raise error if the path is not frozen
        commands.IceboxInitCommand(str(self.test_folder)).run()
        commands.IceboxListCommand().list_local(str(self.test_folder))

        commands.IceboxFreezeCommand(str(self.test_folder)).run()
        icebox = common.utils.FindIcebox(self.test_folder)
        
        # list should work if remote path exists
        commands.IceboxListCommand().list_local(str(self.test_folder))

        # listing should return all frozen files in given remote path
        res: ListResult = commands.IceboxListCommand().list_local(str(self.test_folder))
        self.assertTrue(len(res.folders), 1)
        self.assertEqual(res.folders[0].name,  self.test_subfolder.name)
        self.assertTrue(len(res.files), 1)
        self.assertEqual(res.files[0].name, self.test_folder_file.name)
