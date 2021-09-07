import time

from coolname import generate_slug
from pathlib import Path

from app.elements.icebox import IceboxError
from app.common import utils
from app.elements.icebox import Icebox
from app.elements.icebox import LocalIcebox


class IceboxInitCommand:
    def __init__(self, path: str):
        self.path: Path = utils.ResolvePath(path)

    def run(self) -> Icebox:
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

        # good to go
        return self.__create_icebox(self.path)

    def __create_icebox(self, path: Path) -> Icebox:
        icebox_path: Path = utils.ResolveIcebox(path)
        # raise error if icebox already exists
        if icebox_path.is_file():
            raise IceboxError(
                "Cannot create icebox. Another already exists at "
                f"'{icebox_path}'.")
        # use the path to initialize an icebox
        print(f"Initializing icebox in '{self.path}'...")
        icebox = LocalIcebox(
            id=f"{generate_slug(2)}_{int(time.time())}", path=str(path))
        utils.Finalize(icebox)
        return icebox
