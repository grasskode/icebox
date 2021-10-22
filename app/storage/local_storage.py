import os
import shutil
import typing

from datetime import datetime
from pathlib import Path

from .icebox_storage import IceboxStorage
from .icebox_storage import IceboxStorageError
from app import config
from app.common import utils
from app.elements.icebox import Icebox
from app.elements.icebox_remote_file import IceboxRemoteFile


class LocalStorage(IceboxStorage):
    """Local storage for Icebox.

    This storage uses the local filesystem to store files. Does not add much
    utility but is helpful for testing out workflows.
    """
    def __init__(self, path: str):
        self.storage_path = Path(path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def ListRemote(
            self, rel_path: typing.Optional[str] = None
            ) -> typing.Tuple[
                typing.List[IceboxRemoteFile], typing.List[IceboxRemoteFile]]:
        """List the remote iceboxes.

        If a remote path is provides, it lists the given path in the remote
        storage.

        Returns a tuple and folder and file.

        Raises
            IceboxStorageError
        """
        folders, files = [], []
        path = self.storage_path
        if rel_path:
            path = self.storage_path / Path(rel_path)
        if not path.exists():
            raise IceboxStorageError("Path not found!")
        if path.is_file():
            files.append(IceboxRemoteFile.from_path(str(path), path))
        else:
            for child in path.iterdir():
                child_path = os.path.relpath(
                    str(child), str(self.storage_path))
                if child.is_file():
                    files.append(
                        IceboxRemoteFile.from_path(child_path, child))
                else:
                    # check if child is an icebox
                    icebox = utils.ReadIcebox(child)
                    if icebox:
                        folders.append(
                            IceboxRemoteFile.from_path(child_path, child))
        folders = sorted(folders, key=lambda x: x.name)
        files = sorted(files, key=lambda x: x.name)
        return folders, files

    def List(self, icebox: Icebox, remote_path: str,
             recursive: bool = False) -> typing.Tuple[
             typing.List[IceboxRemoteFile], typing.List[IceboxRemoteFile]]:
        """List the objects in the given icebox withthe given remote path.

        Returns a tuple of directories and files.

        Overrides the default unimplemented method in IceboxStorage.
        """
        dirs, files = [], []
        path = self.storage_path / Path(icebox.id) / Path(remote_path)

        # get all the immediate children of the remote path
        for child in path.iterdir():
            if child.name == config.ICEBOX_FILE_NAME:
                continue
            child_path = os.path.relpath(
                str(child), str(self.storage_path / Path(icebox.id)))
            if child.is_dir():
                dirs.append(
                    IceboxRemoteFile(name=child_path, is_dir=True))
            else:
                updated = datetime.fromtimestamp(child.stat().st_mtime)
                files.append(
                    IceboxRemoteFile(
                        name=child_path, size=child.stat().st_size,
                        updated=updated))
        dirs.sort(key=lambda x: x.name)
        files.sort(key=lambda x: x.name)
        # if recursive and directories were found, list all of them and add
        # result to the return set
        if dirs and recursive:
            dirs_to_recurse = list(dirs)
            for dir in dirs_to_recurse:
                _dirs, _files = self.List(icebox, dir.name, recursive=True)
                dirs.extend(_dirs)
                files.extend(_files)
        return dirs, files

    def Upload(self, source_path: str, relative_destination_path: str):
        """Upload the source_path to the relative_destination_path.

        The source_path should be local and the relative_destination_path
        should be remote. The source_path should point to a file locally.

        Overrides the default unimplemented method in IceboxStorage.

        Raises
            IceboxStorageError
        """
        _source_path = Path(source_path)
        _destination_path = self.storage_path / Path(relative_destination_path)

        # check if source_path is a file
        if not _source_path.is_file():
            raise IceboxStorageError("Source should be a file.")

        # create destination path if it does not exist
        _destination_path.parent.mkdir(parents=True, exist_ok=True)
        _destination_path.touch(exist_ok=True)

        # copy contents
        shutil.copyfile(_source_path, _destination_path)

    def Download(self, relative_source_path: str, destination_path: str):
        """Download the relative_source_path to the destination_path.

        The source path should be remote and the destination path should be
        local. Destination path should not exist or should be a file which will
        be **overwritten**.

        Overrides the default unimplemented method in IceboxStorage.

        Raises
            IceboxStorageError
        """
        _source_path = self.storage_path / Path(relative_source_path)
        _destination_path = Path(destination_path)

        # check if destination_path is not a directory
        if not _destination_path.exists():
            _destination_path.parent.mkdir(parents=True, exist_ok=True)
            _destination_path.touch(exist_ok=True)
        if _destination_path.is_dir():
            raise IceboxStorageError(
                "Destination should not exist or should be a file.")

        # copy contents
        shutil.copyfile(_source_path, _destination_path)

    def Destroy(self):
        """Destroy the storage.

        Utility function.
        """
        shutil.rmtree(self.storage_path)
