from typing import Optional
from google.cloud import storage
import hashlib
from common import IceboxStorageError


class GoogleCloudStorageError(IceboxStorageError):
    pass


class GoogleCloudStorage:

    def __init__(self, cred: str, location: str, bucket_name: str):
        # read credentials from the configuration file
        self._client = storage.Client.from_service_account_json(cred)
        self._location = location
        self._bucket = self._check_or_create_bucket(bucket_name)

    def _check_or_create_bucket(self, bucket_name):
        """The application expects a bucket with given name. Create one if it does not exist already."""
        bucket_names = [b.name for b in self._client.list_buckets()]
        if bucket_name not in bucket_names:
            # create the bucket
            print(f"Creating {bucket_name} in {self._location}...")
            bucket = self._client.create_bucket(bucket_name, self._location, requester_pays=False)
        else:
            bucket = self._client.bucket(bucket_name)
        # disable bucket.requester_pays
        ## TODO: return to requester_pays. Maybe it's a useful idea.
        if bucket.requester_pays:
            print(f"Disabling requester pays on bucket {bucket_name}.")
            bucket.requester_pays = False
            bucket.patch()
        return bucket

    def Upload(self, source_path: str, dest_path: str):
        """Upload a file to the remote location."""
        if not self._bucket:
            raise GoogleCloudStorageError("Bucket not configured!")
        try:
            blob = self._bucket.blob(dest_path)
            blob.upload_from_filename(source_path)
            print(f"File {source_path} uploaded to {dest_path}...")
        except Exception as e:
            print(e)
            raise GoogleCloudStorageError("Error uploading file!")

    def Download(self, source_path: str, dest_path: str):
        """Download a file from the remote location."""
        if not self._bucket:
            raise GoogleCloudStorageError("Bucket not configured!")
        try:
            blob = self._bucket.blob(source_path)
            blob.download_to_filename(dest_path)
            print(f"File {source_path} downloaded to {dest_path}...")
        except Exception as e:
            print(e)
            raise GoogleCloudStorageError("Error downloading file!")
