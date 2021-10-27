from __future__ import annotations

import os

from datetime import datetime
from pathlib import Path
from typing import Any, List

from pydantic import BaseModel

from app.elements.icebox import IceboxError
from app.common import utils
from app.elements.icebox import Icebox
from app.storage.icebox_storage import IceboxStorage
from app.storage.icebox_storage import IceboxStorageError


class IceboxListCommand:
    def __init__(self):
        self.storage: IceboxStorage = utils.GetStorage()

    def run(self, path: str, remote: bool):
        try:
            if remote:
                result = self.list_remote(path)
            else:
                result =self.list_local(path)
            print(result.output)
            
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

    def list_local(self, path: str) -> ListResult:
        """List files assuming the path to be local.
        
        icebox_name
        (* frozen, ~ locally modified)
        total 5
        
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
        print(icebox)
        if not icebox:
            raise IceboxError(
                f"'{p}' is not in an icebox.")

        # good to go
        icebox = utils.Synchronize(icebox)
        relative_path = utils.GetRelativeRemotePath(str(p), icebox.path)
        folders, files = self.storage.List(icebox, relative_path)
        total_items = len(files) + len(folders)
        output = f"{os.linesep}{icebox.id}{os.linesep}"
        output += f"total {total_items}{os.linesep}"
        output += f"(* frozen, ~ locally modified){os.linesep}{os.linesep}"
        for folder in folders:
            output += f"  {folder.name}{os.linesep}"
        for file in files:
            marker = " "
            if file.is_frozen:
                marker = "*"
            if file.is_modified:
                marker = "~"
            output += f"{marker} {file.name}{os.linesep}"
        output += os.linesep
        return ListResult(
            output=output, files=files, folders=folders,
            is_remote=False, icebox=icebox)

    def list_remote(self, path: str) -> ListResult:
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
        output = f"{os.linesep}total {total_items}{os.linesep}{os.linesep}"
        for folder in folders:
            output += f"{folder.name}{os.linesep}"
        for file in files:
            output += f"{file.name}{os.linesep}"
        output += os.linesep
        return ListResult(
            output=output, files=files, folders=folders,
            is_remote=True, icebox=None)


class ListResult(BaseModel):
    output: str
    files: List[Any] = []
    folders: List[Any] = []
    is_remote: bool = False
    icebox: Icebox = None
