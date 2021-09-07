import os
import sys
import typing

from pathlib import Path

from app.elements.icebox import IceboxError
from app.common import utils
from app.elements.icebox import Icebox
from app.storage.icebox_storage import IceboxStorage
from app.storage.icebox_storage import IceboxStorageError


class IceboxThawCommand:
    def __init__(self, path: str):
        self.path: Path = utils.ResolvePath(path)
        self.icebox: Icebox = utils.FindIcebox(self.path)
        self.storage: IceboxStorage = utils.GetStorage()

    def run(self):
        # check if path lies in an icebox path
        if not self.icebox:
            raise IceboxError(
                f"'{self.path}' is not in an icebox! Please initialize first.")
        # path should exist locally or should be present in the icebox
        if (not (self.path and self.path.exists())
                and not utils.ExistsInIcebox(self.path, self.icebox)):
            raise IceboxError("Invalid path!")

        # good to go
        self.icebox = utils.Synchronize(self.icebox)
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
            # Thaw entire icebox.
            filelist = self.icebox.frozen_files
        else:
            # Thaw the files that are children to the given path.
            filelist = [
                f for f in self.icebox.frozen_files
                if f == relpath or f.startswith(relpath + os.sep)]

        # Only retain the files that are not overwritten locally.
        filtered_filelist = []
        for f in filelist:
            localpath = utils.GetAbsoluteLocalPath(f, self.icebox.path)
            if not localpath.exists() or localpath.stat().st_size == 0:
                # Include files that are either not present locally or do not
                # have content.
                filtered_filelist.append(f)
            elif localpath.exists():
                # Skip the files that are non-zero size. These were overwritten
                # locally.
                print(f"Skipping locally overwritten file at {str(f)}.")
        return filtered_filelist

    def __thaw_file(self, relpath: str):
        try:
            self.__download_file(relpath)
        except IceboxStorageError as e:
            # Print error if download was unsuccessful.
            print(e)
            print(f"Unable to thaw {relpath}! Check stack trace for error.")
        else:
            # If successful, remove file's entry from icebox.
            self.icebox.frozen_files.remove(relpath)

    def __download_file(self, relpath: str):
        """Wrapper function to download file.

        Enables testing by mocking.

        Raises
            IceboxStorageError
        """
        # download file
        utils.DownloadFile(self.icebox, relpath, storage=self.storage)
