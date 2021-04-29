import json
import time

from coolname import generate_slug
from pathlib import Path

from app.common import Icebox
from app.common import IceboxError
from app.common import utils


class IceboxInitCommand:
    def __init__(self, path: str):
        self.path: Path = utils.ResolvePath(path)

    def run(self):
        if not self.path or not self.path.exists():
            raise IceboxError("Missing path!")
        # check path for valid folder
        if not self.path.is_dir():
            raise IceboxError("Path is not a directory.")
        # check if path is already part of an icebox
        existing_icebox = utils.FindIcebox(self.path)
        if existing_icebox and existing_icebox.path != self.path:
            raise IceboxError(
                "Path is already part of an icebox at "
                f"'{existing_icebox.path}'. "
                "Cannot create another icebox here.")
        self.__create_icebox(self.path)

    def __create_icebox(self, path: str):
        icebox_path: Path = utils.ResolveIcebox(path)
        # raise error if icebox already exists
        if icebox_path.is_file():
            raise IceboxError(
                "Cannot create icebox. Another already exists at "
                f"'{icebox_path}'.")
        # use the path to initialize an icebox
        print(f"Initializing icebox in '{self.path}'...")
        icebox = Icebox(f"{generate_slug(2)}_{int(time.time())}", path)
        icebox_path.write_text(json.dumps(icebox.to_dict()))
        try:
            utils.UploadFile(icebox, icebox_path)
        except Exception as e:
            print("Error uploading icebox file to remote.")
            # remove icebox file if there was an error uploading
            icebox_path.unlink()
            raise e
