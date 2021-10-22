import os
from typing import List, Tuple

from app.common import utils
from app.elements.icebox_remote_file import IceboxRemoteFile
from app.storage.icebox_storage import IceboxStorage

class IceboxListRemoteCommand:
    # Print something like the following for all iceboxes within the
    # configured storage.
    #
    # total 5
    # 
    # spectacular-numbat_1/
    # spectacular-numbat_2/
    # spectacular_file_1
    # spectacular_file_2
    # spectacular_file_3
    
    def __init__(self):
        self.storage: IceboxStorage = utils.GetStorage()

    def run(self, remote: str = None):
        # no checks required
        folders, files = self.storage.ListRemote(rel_path=remote)
        print(f"{os.linesep}total {len(folders)+len(files)}{os.linesep}")
        for folder in folders:
            print(f"{folder.name}")
        for file in files:
            print(f"{file.name}")
