import enum
import typing

from app.common import IceboxStorageError
from app.elements.icebox_remote_file import IceboxRemoteFile


class IceboxStorageType(enum.Enum):
    LOCAL = 'LOCAL'
    GCP = 'GCP'
    AWS = 'AWS'


class IceboxStorage:
    """Informal interface for all storage classes supported by Icebox."""

    def ListAll(self) -> typing.List[str]:
        """List the remote iceboxes.

        Returns a list remote icebox IDs.

        Raises
            IceboxStorageError
        """
        raise IceboxStorageError("Unimplemented.")

    def List(
            self, remote_path: str, recursive: bool = False
            ) -> typing.Tuple[
                typing.List[IceboxRemoteFile], typing.List[IceboxRemoteFile]]:
        """List the objects in the given remote path.

        Returns a tuple of list of directories and list of files.

        Raises
            IceboxStorageError
        """
        raise IceboxStorageError("Unimplemented.")

    def Upload(self, source_path: str, relative_destination_path: str):
        """Upload the source_path to the relative_destination_path.

        The source_path should be local and the relative_destination_path
        should be remote. The source_path should point to a file locally.

        Raises
            IceboxStorageError
        """
        raise IceboxStorageError("Unimplemented.")

    def Download(self, relative_source_path: str, destination_path: str):
        """Download the relative_source_path to the destination_path.

        The source path should be remote and the destination path should be
        local. Destination path should not exist or should be a file which will
        be **overwritten**.

        Raises
            IceboxStorageError
        """
        raise IceboxStorageError("Unimplemented.")
