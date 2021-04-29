import enum
import typing

from app.common import IceboxStorageError


class IceboxStorageType(enum.Enum):
    LOCAL = 'LOCAL'
    GCP = 'GCP'
    AWS = 'AWS'


class IceboxStorage:
    """Informal interface for all storage classes supported by Icebox."""

    def List(
            self, remote_path: str, recursive: bool = False
            ) -> typing.Tuple[typing.List[str], typing.List[str]]:
        """List the objects in the given remote path.

        Returns a tuple of list of directories and list of files.

        Raises
            IceboxStorageError
        """
        raise IceboxStorageError("Unimplemented.")

    def Upload(self, source_path: str, dest_path: str):
        """Upload the source_path to the destination_path.

        The source_path should be local and the destination_path should be
        remote. The source_path should point to a file locally.

        Raises
            IceboxStorageError
        """
        raise IceboxStorageError("Unimplemented.")

    def Download(self, source_path: str, dest_path: str):
        """Download the source_path to the destination_path.

        The source path should be remote and the destination path should be
        local.

        Raises
            IceboxStorageError
        """
        raise IceboxStorageError("Unimplemented.")
