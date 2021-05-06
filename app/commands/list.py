import os

from datetime import datetime
from pathlib import Path

from app import config
from app.common import IceboxError
from app.common import IceboxStorageError
from app.common import utils
from app.elements.icebox import Icebox
from app.storage.icebox_storage import IceboxStorage


class IceboxListCommand:
    def __init__(self, parent: str, remote: str, recursive: bool = False):
        self.remote = remote
        self.recursive: bool = recursive
        self.path: Path = (
            None if not parent or not remote
            else utils.ResolvePath(os.sep.join([parent, remote])))
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
        print(f"Listing '{self.remote}'...")

        try:
            relative_path = utils.GetRelativeRemotePath(
                self.path, self.icebox.path)
            dirs, files = self.storage.List(
                self.icebox, relative_path, recursive=self.recursive)
            total_items = len(files)
            if not self.recursive:
                total_items += len(dirs)
            print(f"{total_items} items found.")
            if total_items > 0:
                max_size_width = (
                    len(str(max([lf.size for lf in files])))
                    if len(files) > 0 else 1)
                max_time_width = len(
                    datetime.now().strftime(config.ICEBOX_TIME_FORMAT))
                # TODO possibly make the entire listing format configurable
                if not self.recursive:
                    for d in dirs:
                        print(
                            f"{'':{max_size_width}} - {'':{max_time_width}} - "
                            f"{d.name}{os.sep}")
                for lf in files:
                    updated = lf.updated.strftime(config.ICEBOX_TIME_FORMAT)
                    print(
                        f"{lf.size:{max_size_width}} - {updated} - "
                        f"{lf.name}")
        except IceboxStorageError as e:
            print(e)
            print(
                f"Unable to list '{self.remote}''! Check stack trace for "
                "error.")
