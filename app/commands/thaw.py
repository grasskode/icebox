import os
import sys
import typing

from pathlib import Path

from app.common import Icebox
from app.common import IceboxError
from app.common import IceboxStorageError
from app.common import utils
from app.storage.icebox_storage import IceboxStorage


class IceboxThawCommand:
    def __init__(self, path: str):
        self.path: Path = utils.ResolvePath(path)
        self.icebox: Icebox = utils.FindIcebox(self.path)
        self.storage: IceboxStorage = utils.GetStorage()

    def run(self):
        # path should exist locally or should be present in the icebox
        if (not (self.path and self.path.exists())
                and (self.icebox
                     and not utils.ExistsInIcebox(self.path, self.icebox))):
            raise IceboxError("Invalid path!")
        # check if path lies in an icebox path
        if not self.icebox:
            raise IceboxError(
                f"'{self.path}' is not in an icebox! Please initialize first.")

        print(f"Thawing '{self.path}'...")
        # create list of files in the path that need to be thawed
        filelist = self.__get_files_to_thaw()
        # TODO: temporary limit on maximum number of files to thaw at a time.
        # Might not be required so we can remove it later.
        if len(filelist) > 50:
            raise IceboxError("Too many files to thaw!")

        # for each file in filelist, thaw file recursively
        for i in range(len(filelist)):
            sys.stdout.write(
                f"Thawing {i+1}/{len(filelist)} -> {filelist[i]}... \r")
            sys.stdout.flush()
            self.__thaw_file(filelist[i])
        utils.Finalize(self.icebox)

    def __get_files_to_thaw(self) -> typing.List[str]:
        relpath = utils.GetRelativeRemotePath(str(self.path), self.icebox.path)
        if relpath == '.':
            # thaw entire icebox
            filelist = self.icebox.frozen_files
        else:
            filelist = [
                f for f in self.icebox.frozen_files
                if f == relpath or f.startswith(relpath + os.sep)]

        # only retain the files that are not overwritten
        filtered_filelist = []
        for f in filelist:
            localpath = utils.GetAbsoluteLocalPath(f, self.icebox.path)
            if not localpath.exists() or localpath.stat().st_size == 0:
                filtered_filelist.append(f)
            elif localpath.exists():
                # Skip the files that are non zero size. These were overwritten
                # locally.
                print(f"Skipping locally overwritten file at {str(f)}.")
        return filtered_filelist

    def __thaw_file(self, relpath: str):
        try:
            # download file
            utils.DownloadFile(self.icebox, relpath, storage=self.storage)
        except IceboxStorageError as e:
            # print error if download was unsuccessful
            print(e)
            print(f"Unable to thaw {relpath}! Check stack trace for error.")
        else:
            # if successful, remove from icebox
            self.icebox.frozen_files.remove(relpath)
