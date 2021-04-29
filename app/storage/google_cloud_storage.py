import typing

from .icebox_storage import IceboxStorage
from app.common import IceboxStorageError
from app.common import utils

from google.cloud import storage


class GoogleCloudStorage(IceboxStorage):
    """Icebox Storage that uses Google Cloud Storage as the backend."""

    def __init__(self, cred: str, location: str, bucket_name: str):
        # read credentials from the configuration file
        self._client = storage.Client.from_service_account_json(cred)
        self._location = location
        self._bucket = self._check_or_create_bucket(bucket_name)

    def _check_or_create_bucket(self, bucket_name):
        """Checks whether the bucket exists or creates one.

        The application expects a bucket with given name. Create one if it does
        not already exist.
        """
        bucket_names = [b.name for b in self._client.list_buckets()]
        if bucket_name not in bucket_names:
            # create the bucket
            print(f"Creating {bucket_name} in {self._location}...")
            bucket = self._client.create_bucket(
                bucket_name, self._location, requester_pays=False)
        else:
            bucket = self._client.bucket(bucket_name)
        # disable bucket.requester_pays
        # TODO: return to requester_pays. Maybe it's a useful idea.
        if bucket.requester_pays:
            print(f"Disabling requester pays on bucket {bucket_name}.")
            bucket.requester_pays = False
            bucket.patch()
        return bucket

    def List(
            self, remote_path: str, recursive: bool = False
            ) -> typing.Tuple[typing.List[str], typing.List[str]]:
        """List the files in the given remote location."""
        if not self._client:
            raise IceboxStorageError("Client not configured!")
        if not self._bucket:
            raise IceboxStorageError("Bucket not configured!")
        try:
            all_blobs = []
            dirs = []
            # check if the remote_path is a file or directory
            blob = self._bucket.get_blob(remote_path)
            if blob:
                # remote path is a file
                all_blobs.append(blob)
            else:
                # remote_path is not a file or does not exist
                # check if remote_path is a directory
                if not remote_path.endswith(utils.REMOTE_PATH_DELIMITER):
                    remote_path += utils.REMOTE_PATH_DELIMITER
                delimiter = None if recursive else utils.REMOTE_PATH_DELIMITER
                # TODO we are not getting prefixes for some weird reason.
                # Check this.
                blobs = self._client.list_blobs(
                    self._bucket, prefix=remote_path, delimiter=delimiter)
                # print(blobs.prefixes)
                for p in blobs.prefixes:
                    split_path = p.split(utils.REMOTE_PATH_DELIMITER)
                    dirs.append(
                        utils.REMOTE_PATH_DELIMITER.join(split_path[1:]))
                dirs.sort()
                all_blobs = list(blobs)
            files = []
            for b in all_blobs:
                split_path = b.name.split(utils.REMOTE_PATH_DELIMITER)
                files.append({
                    'name': utils.REMOTE_PATH_DELIMITER.join(split_path[1:]),
                    'size': b.size,
                    'updated': b.updated
                })
            return dirs, files
        except Exception as e:
            print(e)
            raise IceboxStorageError("Error listing remote path!")

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
