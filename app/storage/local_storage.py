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
from app.elements.icebox_files import IceboxLocalFile, IceboxRemoteFile


class LocalStorage(IceboxStorage):
    """Local storage for Icebox.

    This storage uses the local filesystem to store files. Does not add much
    utility but is helpful for testing out workflows.
    """
    def __init__(self, path: str):
        self.storage_path = Path(path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

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

    def ListRemote(
            self, path: typing.Optional[str] = None
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
        p = self.storage_path
        if path:
            p = self.storage_path / Path(path)
        if not p.exists():
            raise IceboxStorageError("Path not found!")
        if p.is_file():
            files.append(_remote_from_path(str(p), p))
        else:
            for child in p.iterdir():
                child_path = os.path.relpath(
                    str(child), str(p))
                if child.is_file():
                    if child_path != config.ICEBOX_FILE_NAME:
                        files.append(_remote_from_path(child_path, child))
                else:
                    folders.append(_remote_from_path(child_path, child))
        folders = sorted(folders, key=lambda x: x.name)
        files = sorted(files, key=lambda x: x.name)
        return folders, files

    def List(
            self, icebox: Icebox, relpath: str
    ) -> typing.Tuple[
            typing.List[IceboxLocalFile], typing.List[IceboxLocalFile]]:
        """List the objects in the given icebox path.

        Returns a tuple of folders and files.

        TODO: This is untested!

        Raises
            IceboxStorageError
        """

        path = (Path(icebox.path) / Path(relpath)).resolve()
        if not path.exists():
            raise IceboxStorageError(f"'{str(path)}' does not exist.")

        folders, files = [], []
        if path.is_file():
            ilf = _local_from_path(str(path), path)
            if ilf:
                if relpath in icebox.frozen_files:
                    ilf.is_frozen = True
                    if ilf.size > 0:
                        ilf.is_modified = True
                files.append(ilf)
        else:
            for child in path.iterdir():
                child_path = os.path.relpath(
                    str(child), str(icebox.path))
                if child.is_file():
                    ilf = _local_from_path(child_path, Path(child))
                    if ilf:
                        if child_path in icebox.frozen_files:
                            ilf.is_frozen = True
                            if ilf.size > 0:
                                ilf.is_modified = True
                        files.append(ilf)
                else:
                    folders.append(_local_from_path(child_path, Path(child)))
        folders = sorted(folders, key=lambda x: x.name)
        files = sorted(files, key=lambda x: x.name)
        return folders, files


def _remote_from_path(name: str, path: Path) -> IceboxRemoteFile:
    if path.is_dir():
        if not name.endswith(config.REMOTE_PATH_DELIMITER):
            name = f"{name}{config.REMOTE_PATH_DELIMITER}"
        return IceboxRemoteFile(
            name=name, is_dir=True)
    else:
        return IceboxRemoteFile(
            name=name, size=path.stat().st_size,
            updated=datetime.fromtimestamp(path.stat().st_mtime))


def _local_from_path(name: str, path: Path) -> IceboxLocalFile:
    if path.is_dir():
        if not name.endswith(config.REMOTE_PATH_DELIMITER):
            name = f"{name}{config.REMOTE_PATH_DELIMITER}"
        return IceboxLocalFile(
            name=name, is_dir=True)
    else:
        if name == config.ICEBOX_FILE_NAME:
            return None
        return IceboxLocalFile(
            name=name, size=path.stat().st_size,
            updated=datetime.fromtimestamp(path.stat().st_mtime))
