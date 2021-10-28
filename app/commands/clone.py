import shutil
from pathlib import Path

from app import config
from app.common import utils
from app.elements.icebox import IceboxError
from app.storage.icebox_storage import IceboxStorage

class IceboxCloneCommand:
    def __init__(self, icebox: str, path: str):
        self.icebox = icebox
        self.path: Path = utils.ResolvePath(path)
        self.storage: IceboxStorage = utils.GetStorage()

    def run(self) -> None:
        # ensure that the icebox exists
        folders, _ = self.storage.ListRemote()
        icebox_name = self.icebox
        if not icebox_name.endswith(config.REMOTE_PATH_DELIMITER):
            icebox_name = f"{icebox_name}{config.REMOTE_PATH_DELIMITER}"
        exists = False
        for f in folders:
            if f.name == icebox_name:
                exists = True
                break
        if not exists:
            raise IceboxError(f"No icebox named '{self.icebox} found!'")

        # ensure that the path is a fresh folder
        if self.path.exists():
            raise IceboxError(f"'{str(self.path)} already exists!'")

        # ensure that the path is not inside an existing icebox
        existing_icebox = utils.FindIcebox(self.path.parent)
        if existing_icebox:
            raise IceboxError(
                "Cannot clone inside an icebox. Found an existing one at "
                f"'{existing_icebox.path}'.")

        # good to go
        try:
            self.path.mkdir(parents=False, exist_ok=False)
            utils.CloneIcebox(self.icebox, self.path, storage=self.storage)
        except Exception as e:
            shutil.rmtree(self.path, ignore_errors=True)
            print(e)
            print(
                f"Unable to clone icebox! Check stack trace for "
                "error.")
