import json
import os
import typing
from datetime import datetime
from pathlib import Path

from app import config
from app.elements.icebox import Icebox
from app.elements.icebox_files import IceboxLocalFile, IceboxRemoteFile

from .icebox_storage import IceboxStorage
from .icebox_storage import IceboxStorageError
from app.common import utils

from google.cloud import storage


class GoogleCloudStorage(IceboxStorage):
    """Icebox Storage that uses Google Cloud Storage as the backend."""

    def __init__(self, cred: str, location: str, bucket_name: str):
        # read credentials from the configuration file
        self._client = storage.Client.from_service_account_json(cred)
        self._location = location
        with open(cred) as f:
            cred_json = json.load(f)
            self.project_id = cred_json['project_id']
        self._bucket = self._check_or_create_bucket(bucket_name)
        self._bucket_name = bucket_name

    def _check_or_create_bucket(self, bucket_name):
        """Checks whether the bucket exists or creates one.

        The application expects a bucket with given name. Create one if it does
        not already exist.
        """
        bucket_names = [b.name for b in self._client.list_buckets()]
        if bucket_name not in bucket_names:
            # create the bucket
            print(f"Creating {bucket_name} in {self._location}...")
            self._client.create_bucket(
                bucket_name, self._location)

        bucket = self._client.bucket(bucket_name, user_project=self.project_id)
        # disable bucket.requester_pays
        # TODO: return to requester_pays. Maybe it's a useful idea.
        # TODO: this is not working for whatever reason. Check.
        if bucket.requester_pays:
            print(f"Disabling requester pays on bucket {bucket_name}.")
            bucket.requester_pays = False
            bucket.patch()
        return bucket

    def Upload(self, source_path: str, dest_path: str):
        """Upload a file to the remote location."""
        if not self._bucket:
            raise IceboxStorageError("Bucket not configured!")
        try:
            blob = self._bucket.blob(dest_path)
            blob.upload_from_filename(source_path)
            print(f"File {source_path} uploaded to {dest_path}...")
        except Exception as e:
            print(e)
            raise IceboxStorageError("Error uploading file!")

    def Download(self, source_path: str, dest_path: str):
        """Download a file from the remote location."""
        if not self._bucket:
            raise IceboxStorageError("Bucket not configured!")
        try:
            blob = self._bucket.blob(source_path)
            blob.download_to_filename(dest_path)
            print(f"File {source_path} downloaded to {dest_path}...")
        except Exception as e:
            print(e)
            raise IceboxStorageError("Error downloading file!")

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
        if not self._client:
            raise IceboxStorageError("Client not configured!")
        
        delimiter = config.REMOTE_PATH_DELIMITER
        if path and not path.endswith(delimiter):
            path = f"{path}{delimiter}"
        
        folders, files = [], []
        blobs = self._client.list_blobs(
            self._bucket_name, prefix=path, delimiter=delimiter)
        for blob in blobs:
            name = blob.name[len(path):] if path else blob.name
            if name != config.ICEBOX_FILE_NAME:
                files.append(
                    IceboxRemoteFile(name=name,
                    size=blob.size, updated=blob.updated))
        for prefix in blobs.prefixes:
            name = prefix[len(path):] if path else prefix
            folders.append(
                IceboxRemoteFile(name=name, is_dir=True))
        return folders, files

    def List(
            self, icebox: Icebox, relpath: str
    ) -> typing.Tuple[
            typing.List[IceboxLocalFile], typing.List[IceboxLocalFile]]:
        """List the objects in the given icebox path.

        Returns a tuple of folders and files.

        Raises
            IceboxStorageError
        """
        
        path = (Path(icebox.path) / Path(relpath)).resolve()
        if not path.exists():
            raise IceboxStorageError(f"'{str(path)}' does not exist.")
        
        folders, files = [], []
        if path.is_file():
            ilf = _from_path(path)
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
                    ilf = _from_path(Path(child))
                    if ilf:
                        if child_path in icebox.frozen_files:
                            ilf.is_frozen = True
                            if ilf.size > 0:
                                ilf.is_modified = True
                        files.append(ilf)
                else:
                    folders.append(_from_path(Path(child)))
        folders = sorted(folders, key=lambda x: x.name)
        files = sorted(files, key=lambda x: x.name)
        return folders, files


def _from_path(path: Path) -> IceboxLocalFile:
    path = path.resolve()
    if path.is_dir():
        return IceboxLocalFile(
            name=f"{path.name}{os.sep}", is_dir=True)
    else:
        if path.name == config.ICEBOX_FILE_NAME:
            return None
        return IceboxLocalFile(
            name=path.name,
            size=path.stat().st_size,
            updated=datetime.fromtimestamp(path.stat().st_mtime))
