import os
import glob
import sys
from common import IceboxError
from common import IceboxStorageError
from common import utils
from typing import List

class IceboxThawCommand:
    def __init__(self, path=None):
        self.path = utils.ResolvePath(path)
        self.icebox = utils.FindIcebox(path)
        self.storage = utils.GetStorage()

    def run(self):
        if not self.path:
            raise IceboxError("Missing path!")
        # check if path lies in an icebox path
        if not self.icebox:
            raise IceboxError(f"'{self.path}' is not in an icebox! Please initialize first.")
        print(f"Thawing '{self.path}'...")
        # create list of files in the path that need to be thawed
        filelist = self._get_files_to_thaw()
        ## TODO: temporary limit on maximum number of files to thaw at a time. Might not be required so we can remove it later.
        if len(filelist) > 50:
            raise IceboxError("Too many files to thaw!")
        # for each file in filelist, thaw file recursively
        for i in range(len(filelist)):
            sys.stdout.write(f"Thawing {i+1}/{len(filelist)} -> {filelist[i]}... \r")
            sys.stdout.flush()
            self._thaw_file(filelist[i])
        utils.Finalize(self.icebox)

    def _get_files_to_thaw(self) -> List[str]:
        return list(filter(lambda x: x.startswith(self.path), self.icebox.frozen_files))

    def _thaw_file(self, filepath: str):
        try:
            # delete file if it exists
            ## TODO: this is potentially dangerous. We can create a backup and delete once the download is successful.
            os.remove(filepath)
            # download file
            utils.DownloadFile(self.icebox, filepath, storage = self.storage)
        except IceboxStorageError as e:
            # print error if download was unsuccessful
            print(e)
            print(f"Unable to thaw {filepath}! Check stack trace for error.")
        else:
            # if successful, remove from icebox
            self.icebox.frozen_files.remove(filepath)
