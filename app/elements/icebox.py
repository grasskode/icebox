import pydantic
import typing

from pathlib import Path


class Icebox(pydantic.BaseModel):
    """Encapsulation for the icebox class.

    This class is extended by LocalIcebox for the local version.
    """

    id: str
    frozen_files: typing.List[str] = []

    # TODOs:
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
    # * frozen_files should be a set
    # * files should contain more than a simple list of path. Perhaps
    # metadata and a date of freeze.

    def is_valid(self) -> bool:
        return self.id


class LocalIcebox(Icebox):
    """The local manifestation of the icebox.

    Contains an additional field to represent the path.
    """
    path: str

    def is_valid(self) -> bool:
        return super().is_valid() and self.path and Path(self.path).is_dir()


class IceboxError(Exception):
    def __init__(self, message):
        self.message = message
