import os
import glob
import sys
from common import IceboxError
from common import IceboxStorageError
from common import utils

class IceboxFreezeCommand:
    def __init__(self, path=None):
        self.path = utils.ResolvePath(path)
        self.icebox = utils.FindIcebox(path)
        self.storage = utils.GetStorage()

    def run(self):
        if not self.path or not os.path.exists(self.path):
            raise IceboxError("Missing path!")
        # check if path lies in an icebox path
        if not self.icebox:
            raise IceboxError(f"'{self.path}' is not in an icebox! Please initialize first.")
        print(f"Freezing '{self.path}'...")
        # create list of files in the path that need to be frozen
        filelist = self._get_files_to_freeze()
        ## TODO: temporary limit on maximum number of files to freeze at a time. Might not be required so we can remove it later.
        if len(filelist) > 50:
            raise IceboxError("Too many files to freeze!")
        # for each file in filelist, freeze file recursively
        for i in range(len(filelist)):
            sys.stdout.write(f"Freezing {i+1}/{len(filelist)} -> {filelist[i]}... \r")
            sys.stdout.flush()
            self._freeze_file(filelist[i])
        utils.Finalize(self.icebox)

    def _get_files_to_freeze(self):
        filelist = []
        if os.path.isdir(self.path):
            filelist = [f for f in glob.glob(f"{self.path}{os.sep}**{os.sep}*", recursive=True) if os.path.isfile(f)]
        elif os.path.isfile(path):
            filelist = [path]
        # filter out files that have already been frozen
        ## TODO: frozen files might have been locally overwritten. Saving file metadata would help in identifying such cases.
        return list(filter(lambda x: x not in self.icebox.frozen_files, filelist))

    def _freeze_file(self, filepath: str):
        try:
            # upload file
            utils.UploadFile(self.icebox, filepath, storage = self.storage)
        except IceboxStorageError as e:
            # print error if upload was unsuccessful
            print(e)
            print(f"Unable to freeze {filepath}! Check stack trace for error.")
        else:
            # if successful, add to icebox
            self.icebox.frozen_files.append(filepath)
            # replace local with a metadata / preview file
            utils.ReplaceFile(filepath)
