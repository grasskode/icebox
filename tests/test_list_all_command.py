import shutil
import unittest

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=(Path('.') / '.env_test'))

from .utils import TestUtils
from app import commands
from app import common
from app.elements.icebox import Icebox
from app.storage import local_storage

test_utils = TestUtils()


class ListAllCommandTest(unittest.TestCase):

    storage: local_storage.LocalStorage

    @classmethod
    def setUpClass(cls):
        # set up local storage
        cls.storage = common.utils.GetStorage()

    def setUp(self):
        # set up the directory structure
        self.test_folder_1 = test_utils.CreateTestFolder(
            'folder_1')
        self.test_folder_2 = test_utils.CreateTestFolder(
            'folder_2')
        self.test_folder_3 = test_utils.CreateTestFolder(
            'folder_3')

    @classmethod
    def tearDownClass(cls):
        # destroy local storage
        cls.storage.Destroy()

    def tearDown(self):
        # tear down the directory structure
        test_utils.DeleteFolderAndContents(self.test_folder_1)
        test_utils.DeleteFolderAndContents(self.test_folder_2)
        test_utils.DeleteFolderAndContents(self.test_folder_3)

    def test_list_all(self):
        # ListAllCommand does not require any args
        list_all_command = commands.IceboxListAllCommand()

        # list_all should not return any iceboxes when there are none
        # initialized
        self.assertEqual(len(list_all_command.list_all()), 0)

        # any initialized icebox should immediately reflect in list_all
        commands.IceboxInitCommand(str(self.test_folder_1)).run()
        icebox_1 = common.utils.FindIcebox(self.test_folder_1)
        iceboxes = list_all_command.list_all()
        self.assertEqual(len(iceboxes), 1)
        self.assertIsInstance(iceboxes[0], Icebox)
        self.assertIn(icebox_1.id, [i.id for i in iceboxes])
        commands.IceboxInitCommand(str(self.test_folder_2)).run()
        icebox_2 = common.utils.FindIcebox(self.test_folder_2)
        iceboxes = list_all_command.list_all()
        self.assertEqual(len(iceboxes), 2)
        self.assertIn(icebox_2.id, [i.id for i in iceboxes])
        commands.IceboxInitCommand(str(self.test_folder_3)).run()
        icebox_3 = common.utils.FindIcebox(self.test_folder_3)
        iceboxes = list_all_command.list_all()
        self.assertEqual(len(iceboxes), 3)
        self.assertIn(icebox_3.id, [i.id for i in iceboxes])

        # list_all should show an icebox even if it is deleted locally
        shutil.rmtree(self.test_folder_1)
        self.assertFalse(self.test_folder_1.exists())
        iceboxes = list_all_command.list_all()
        self.assertIsNone(common.utils.FindIcebox(self.test_folder_1))
        self.assertEqual(len(iceboxes), 3)
        self.assertIn(icebox_1.id, [i.id for i in iceboxes])
