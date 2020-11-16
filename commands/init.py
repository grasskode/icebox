import os
from common import IceboxError
from common import utils

class IceboxInitCommand:
    def __init__(self, path=None):
        self.path = utils.ResolvePath(path)

    def run(self):
        if not self.path or not os.path.exists(self.path):
            raise IceboxError("Missing path!")
        # check path for valid folder
        if not os.path.isdir(self.path):
            raise IceboxError("Path is not a directory.")
        # check if path is already part of an icebox
        existing_icebox = utils.FindIcebox(self.path)
        if existing_icebox and existing_icebox.path != self.path:
            raise IceboxError(f"Path is already part of an icebox at '{existing_icebox.path}'. Cannot create another icebox here.")
        print(f"Initializing icebox in '{self.path}'...")
        icebox = utils.CreateIcebox(self.path)
