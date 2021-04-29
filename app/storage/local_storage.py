import shutil
import typing

from pathlib import Path

from .icebox_storage import IceboxStorage
from app.common import IceboxStorageError
from app.common import utils


class LocalStorage(IceboxStorage):
    """Local storage for Icebox.

    This storage uses the local filesystem to store files. Does not add much
    utility but is helpful for testing out workflows.
    """
    def __init__(self, path: str):
        self.storage_path = Path(path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def List(
            self, remote_path: str, recursive: bool = False
            ) -> typing.Tuple[typing.List[str], typing.List[str]]:
        """List the objects in the given remote path.

        Returns a tuple of list of directories and list of files.

        Overrides the default unimplemented method in IceboxStorage.
        """
        dirs, files = [], []
        path = self.storage_path / Path(remote_path)

        # get all the immediate children of the remote path
        for child in path.iterdir():
            child_path = utils.GetRelativeRemotePath(
                str(child), str(self.storage_path))
            if child.is_dir():
                dirs.append(child_path)
            else:
                files.append(child_path)

        # if recursive and directories were found, list all of them and add
        # result to the return set
        if dirs and recursive:
            dirs_to_recurse = list(dirs)
            for dir in dirs_to_recurse:
                _dirs, _files = self.List(dir, recursive=True)
                dirs.extend(_dirs)
                files.extend(_files)
        return dirs, files

    def Upload(self, source_path: str, destination_path: str):
        """Upload the source_path to the destination_path.

        The source_path should be local and the destination_path should be
        remote. The source_path should point to a file locally.

        Overrides the default unimplemented method in IceboxStorage.

        Raises
            IceboxStorageError
        """
        _source_path = Path(source_path)
        _destination_path = self.storage_path / Path(destination_path)

        # check if source_path is a file
        if not _source_path.is_file():
            raise IceboxStorageError("Source should be a file.")

        # create destination path if it does not exist
        _destination_path.parent.mkdir(parents=True, exist_ok=True)
        _destination_path.touch(exist_ok=True)

        # copy contents
        shutil.copyfile(_source_path, _destination_path)

    def Download(self, source_path: str, destination_path: str):
        """Download the source_path to the destination_path.

        The source path should be remote and the destination path should be
        local. Destination path should not exist or should be a file.

        Raises
            IceboxStorageError
        """
        _source_path = self.storage_path / Path(source_path)
        _destination_path = Path(destination_path)

        # check if destination_path is not a directory
        if not _destination_path.exists():
            _destination_path.parent.mkdir(parents=True, exist_ok=True)
            _destination_path.touch(exist_ok=True)
        if _destination_path.is_dir():
            raise IceboxStorageError(
                "Destination should not exist or be a file.")

        # copy contents
        shutil.copyfile(_source_path, _destination_path)

    def Destroy(self):
        """Destroy the storage."""
        shutil.rmtree(self.storage_path)
