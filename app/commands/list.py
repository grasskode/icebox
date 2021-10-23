import os

from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from app import config
from app.elements.icebox import IceboxError
from app.common import utils
from app.elements.icebox import Icebox
from app.elements.icebox_files import IceboxRemoteFile
from app.storage.icebox_storage import IceboxStorage
from app.storage.icebox_storage import IceboxStorageError


class IceboxListCommand:
    def __init__(self):
        self.storage: IceboxStorage = utils.GetStorage()

    def run(self, path: str, remote: bool):
        try:
            if remote:
                self.list_remote(path)
            else:
                self.list_local(path)
            
            # TODO: alternate formatting option
            # max_time_width = len(
            #     datetime.now().strftime(config.ICEBOX_TIME_FORMAT))
            # for lf in files:
            #     updated = lf.updated.strftime(config.ICEBOX_TIME_FORMAT)
            #     print(
            #         f"{lf.size:{max_size_width}} - {updated} - "
            #         f"{lf.name}")
        except IceboxStorageError as e:
            print(e)
            print(
                f"Unable to list path! Check stack trace for "
                "error.")

    def list_local(self, path: str):
        """List files assuming the path to be local.

        total 5
        (* frozen, ~ locally modified)
        
          spectacular-numbat_1/
          spectacular-numbat_2/
        * spectacular_file_1
        ~ spectacular_file_2
          spectacular_file_3
        """
        # check if path is absolute or relative
        p = Path(os.getcwd())
        if path:
            p = Path(path).resolve()
            if not p.exists():
                p = (Path(os.getcwd()) / p).resolve()
            if not p.exists():
                raise IceboxError(
                    f"{path} not found locally.")

        # validate icebox for path
        icebox = utils.FindIcebox(p)
        if not icebox:
            raise IceboxError(
                f"'{p}' is not in an icebox.")

        # good to go
        icebox = utils.Synchronize(icebox)
        relative_path = utils.GetRelativeRemotePath(str(p), icebox.path)
        folders, files = self.storage.List(icebox, relative_path)
        total_items = len(files) + len(folders)
        print(f"{os.linesep}total {total_items}")
        print(f"(* frozen, ~ locally modified){os.linesep}")
        for folder in folders:
            print(f"  {folder.name}")
        for file in files:
            marker = " "
            if file.is_frozen:
                marker = "*"
            if file.is_modified:
                marker = "~"
            print(f"{marker} {file.name}")

    def list_remote(self, path: str):
        """Print remote iceboxes.

        Print contents of the mentioned remote path. Print all iceboxes
        within the configured storage if no path is given.
        
        total 5
        
        spectacular-numbat_1/
        spectacular-numbat_2/
        spectacular_file_1
        spectacular_file_2
        spectacular_file_3
        """
        
        folders, files = self.storage.ListRemote(path=path)
        total_items = len(files) + len(folders)
        print(f"{os.linesep}total {total_items}{os.linesep}")
        for folder in folders:
            print(f"{folder.name}")
        for file in files:
            print(f"{file.name}")
