import json
import unittest

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=(Path('.') / '.env_test'))

from .utils import TestUtils
from app import commands
from app import common
from app import config
from app.storage import local_storage

test_utils = TestUtils()


class IceboxUtilsTest(unittest.TestCase):

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

    @classmethod
    def tearDownClass(cls):
        # destroy local storage
        cls.storage.Destroy()

    def tearDown(self):
        # delete the directory structure
        test_utils.DeleteFolderAndContents(self.test_folder)

    def test_find_icebox(self):
        # no icebox should be found on uninitialized folder
        self.assertIsNone(common.utils.FindIcebox(self.test_folder))

        # icebox should be found in initialized folder
        commands.IceboxInitCommand(str(self.test_folder)).run()
        icebox_parent = common.utils.FindIcebox(self.test_folder)
        self.assertIsNotNone(icebox_parent)
        self.assertEqual(icebox_parent.path, str(self.test_folder))

        # icebox should be found in a subfolder of the initialized folder
        icebox = common.utils.FindIcebox(self.test_subfolder)
        self.assertIsNotNone(icebox)
        self.assertEqual(icebox.path, str(self.test_folder))
        self.assertEqual(icebox.id, icebox_parent.id)

    def test_finalize(self):
        # initialize and get icebox
        commands.IceboxInitCommand(str(self.test_folder)).run()
        icebox = common.utils.FindIcebox(str(self.test_folder))
        self.assertIsNotNone(icebox)
        temp_file = self.test_folder / "temp_file"
        remote_path = (f"{icebox.id}{config.REMOTE_PATH_DELIMITER}"
                       f"{config.ICEBOX_FILE_NAME}")

        # Finalize requires an icebox.
        with self.assertRaises(common.IceboxError):
            common.utils.Finalize(None)

        # any changes made locally should reflect in remote after finalize
        test_string = "something random"
        icebox.frozen_files.append(test_string)
        common.utils.Finalize(icebox)
        IceboxUtilsTest.storage.Download(remote_path, str(temp_file))
        with open(str(temp_file), 'r') as f:
            icebox_remote_data = json.load(f)
        self.assertEqual(icebox_remote_data['id'], icebox.id)
        self.assertIn(test_string, icebox_remote_data['frozen_files'])

    def test_synchronize(self):
        # initialize and get icebox
        commands.IceboxInitCommand(str(self.test_folder)).run()
        icebox = common.utils.FindIcebox(str(self.test_folder))
        data = icebox.dict()
        self.assertIsNotNone(icebox)
        temp_file = self.test_folder / "temp_file"
        remote_path = (f"{icebox.id}{config.REMOTE_PATH_DELIMITER}"
                       f"{config.ICEBOX_FILE_NAME}")

        # Synchronize requires an icebox.
        with self.assertRaises(common.IceboxError):
            common.utils.Synchronize(None)

        # synchronize should throw error if the remote icebox contents are
        # invalid
        with open(temp_file, 'w') as f:
            f.write("Random string that is not an icebox.")
        IceboxUtilsTest.storage.Upload(str(temp_file), remote_path)
        with self.assertRaises(common.IceboxError):
            common.utils.Synchronize(icebox)

        # any valid changes made remotely should reflect locally after
        # synchronize
        test_string = "something random"
        self.assertNotIn(test_string, data['frozen_files'])
        data['frozen_files'].append(test_string)
        with open(temp_file, 'w') as f:
            json.dump(data, f)
        IceboxUtilsTest.storage.Upload(str(temp_file), remote_path)
        icebox = common.utils.Synchronize(icebox)
        self.assertIn(test_string, icebox.frozen_files)
