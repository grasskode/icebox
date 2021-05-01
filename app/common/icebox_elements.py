from datetime import datetime

import pydantic
import typing

from app.storage.icebox_storage import IceboxStorageType


class IceboxConfig(pydantic.BaseModel):
    storage_choice: IceboxStorageType = None
    storage_options: typing.Dict[str, str] = None


class IceboxRemoteFile(pydantic.BaseModel):
    name: str
    size: int = 0
    updated: datetime = 0
    is_dir: bool = False


class Icebox:
    def __init__(
            self, id: str, path: str, frozen_files: typing.List[str] = []):
        # TODO:
        # * Every Icebox should have a unique identifier (possibly human
        # readable). This path will be machine dependant and should not be
        # used. Ideally a remote icebox should map to a local path and this
        # information should be stored within the machine.
        # * Think of adding this to the init process. Whenever an icebox is
        # init, it is assigned an id. The local .icebox file created contains
        # the path (or might not need to) and the remote simply contains the
        # ID.
        # * Adding path to .icebox makes us sure that moving the file around
        # would not affect operations.
        # * Also think about inconsistencies like frozen file deleted from
        # local (should be deleted from remote?). Possibly push and pull
        # functionalities. Ormaybe sync can do this as well. If the remote and
        # local are already configured, it simply gets the information in a
        # consistent state.
        self.id = id
        self.path = path
        # TODO: frozen_files should be a set
        # TODO: files should contain more than a simple list of path. Perhaps
        # metadata and a date of freeze.
        self.frozen_files = frozen_files

    def to_dict(self):
        return {
            'id': self.id,
            'frozen_files': self.frozen_files
        }

    @classmethod
    def from_dict(cls, path, dict):
        return Icebox(
            id=dict['id'], path=path, frozen_files=dict.get('frozen_files'))
