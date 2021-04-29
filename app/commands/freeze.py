import sys
import typing

from pathlib import Path

from app import config
from app.common import Icebox
from app.common import IceboxError
from app.common import IceboxStorageError
from app.common import utils
from app.storage.icebox_storage import IceboxStorage


class IceboxFreezeCommand:
    def __init__(self, path: str):
        self.path: Path = utils.ResolvePath(path)
        self.icebox: Icebox = utils.FindIcebox(self.path)
        self.storage: IceboxStorage = utils.GetStorage()

    def run(self):
        if not self.path or not self.path.exists():
            raise IceboxError("Missing path!")
        # check if path lies in an icebox path
        if not self.icebox:
            raise IceboxError(
                f"'{self.path}' is not in an icebox! Please initialize first.")
        print(f"Freezing '{self.path}'...")

        # create list of files in the path that need to be frozen
        filelist = self.__get_files_to_freeze()
        # TODO: temporary limit on maximum number of files to freeze at a
        # time. Might not be required so we can remove it later.
        if len(filelist) > 50:
            raise IceboxError("Too many files to freeze!")

        # for each file in filelist, freeze file recursively
        for i in range(len(filelist)):
            sys.stdout.write(
                f"Freezing {i+1}/{len(filelist)} -> {filelist[i]}... \r")
            sys.stdout.flush()
            self.__freeze_file(filelist[i])
        utils.Finalize(self.icebox)

    def __get_files_to_freeze(self) -> typing.List[str]:
        filelist = []
        if self.path.is_dir():
            filelist = [f for f in sorted(self.path.glob("**/*"))
                        if f.is_file() and f.stem != config.ICEBOX_FILE_NAME]
        else:
            filelist = [self.path]
        # filter out files that have already been frozen
        # TODO: frozen files might have been locally overwritten. Saving file
        # metadata would help in identifying such cases.
        filtered_filelist = []
        for f in filelist:
            if (utils.GetRelativeRemotePath(str(f), self.icebox.path)
                    in self.icebox.frozen_files):
                if f.stat().st_size == 0:
                    print(f"Skipping frozen file at {str(f)}.")
                else:
                    # TODO introduce flag or env variable to change
                    # this behaviour.
                    print(f"Found locally overwritten file at {str(f)}.")
                    filtered_filelist.append(f)
            else:
                filtered_filelist.append(f)
        return filtered_filelist

    def __freeze_file(self, filepath: str):
        try:
            # upload file
            utils.UploadFile(self.icebox, filepath, storage=self.storage)
        except IceboxStorageError as e:
            # print error if upload was unsuccessful
            print(e)
            print(f"Unable to freeze {filepath}! Check stack trace for error.")
        else:
            # if successful, add to icebox
            self.icebox.frozen_files.append(
                utils.GetRelativeRemotePath(filepath, self.icebox.path))
            # replace local with a metadata / preview file
            utils.ReplaceFile(filepath)
