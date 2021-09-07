from coolname import generate_slug
from typing import Dict

from app.common import utils
from app.elements.icebox import IceboxError
from app.elements.icebox_config import IceboxConfig
from app.storage.google_cloud_storage import GoogleCloudStorage
from app.storage.icebox_storage import IceboxStorageType


class IceboxConfigCommand:
    def __init__(self):
        self.config: IceboxConfig = utils.ReadConfig()

    def run(self):
        # check if config file already exists
        if not self.config:
            self.config = IceboxConfig()
        # get storage choice if it does not exist
        if not self.config.storage_choice:
            self.config.storage_choice = self._get_storage_choice()
        # configure the storage
        if self.config.storage_choice == IceboxStorageType.GCP:
            if not self.config.storage_options:
                self.config.storage_options = self._create_gcp_config()
            else:
                self._configure_gcp(self.config.storage_options)
        elif self.config.storage_choice == 'AWS':
            if not self.config.storage_options:
                self.config.storage_options = self._create_aws_config()
            else:
                self._configure_aws(self.config.storage_options)
        else:
            raise IceboxError("Unknown storage choice!")
        utils.WriteConfig(self.config)

    def _get_storage_choice(self) -> IceboxStorageType:
        """Ask the user to input their choice of storage options."""
        storage_choice = 0
        while storage_choice not in range(1, 3):
            if storage_choice == 0:
                print("Choose a cloud storage service provider:")
            else:
                print("Invalid choice. Choose from one of the following:")
            print("""\t[1] Google Cloud Storage (GCP)
\t[2] Amazon S3 (AWS)
Enter your choice [1]:""", end=" ")
            input_str = input()
            if not input_str:
                storage_choice = 1
            else:
                try:
                    storage_choice = int(input_str)
                except ValueError:
                    storage_choice = -1
        if storage_choice == 1:
            return IceboxStorageType.GCP
        elif storage_choice == 2:
            return IceboxStorageType.AWS
        else:
            raise IceboxError("Unknown storage choice!")

    def _create_gcp_config(self) -> Dict[str, str]:
        """Create and save the GCP configuration.

        Ask the user to input GCP credentials and store them in the icebox
        config file.

        Raises
            TODO
        """
        def _get_gcp_credentials_filepath() -> str:
            creds_filepath = "~/.iceboxcfg/gcp/creds.json"
            print(
                "Enter path for the GCP service account credentials "
                f"[{creds_filepath}]:", end=" ")
            input_creds_filepath = input().strip()
            if input_creds_filepath != '':
                creds_filepath = input_creds_filepath
            return creds_filepath

        def _get_gcp_preferred_location() -> str:
            location = "asia-south1"
            print(
                "Enter preferred GCP location ("
                "https://cloud.google.com/storage/docs/locations) "
                f"[{location}]:", end=" ")
            input_location = input().strip()
            if input_location != '':
                location = input_location
            return location

        def _get_gcp_bucket_name() -> str:
            # TODO: make the slug length and prefix configurable.
            prefix = "icebox_"
            bucket_name = generate_slug(3)
            print(
                "Enter a unique bucket name or map to an existing one. Leave "
                f"blank to use auto generated name ({bucket_name}):", end=" ")
            input_bucket_name = input().strip()
            if input_bucket_name != '':
                bucket_name = input_bucket_name
            # add prefix to identify an icebox bucket
            if not bucket_name.startswith(prefix):
                bucket_name = f"{prefix}{bucket_name}"
            return bucket_name

        cred = utils.ResolvePath(_get_gcp_credentials_filepath())
        if not cred.is_file():
            raise IceboxError(
                "Credentials file does not exist at mentioned path.")
        location = _get_gcp_preferred_location()
        bucket_name = _get_gcp_bucket_name()

        # Attempt to create storage client using the given credentials
        gcp_config = {
            'bucket': bucket_name,
            'credentials': str(cred),
            'default_location': location
        }
        self._configure_gcp(gcp_config)
        return gcp_config

    def _configure_gcp(self, storage_config: Dict[str, str]):
        """Configure GoogleCloudStorage to check for any errors.

        Raises
            TODO
        """
        # print("Checking access permissions.")
        GoogleCloudStorage(
            storage_config['credentials'],
            storage_config['default_location'],
            storage_config['bucket'])

    def _create_aws_config(self):
        raise IceboxError("Not implemented!")

    def _configure_aws(self, storage_config: Dict[str, str]):
        raise IceboxError("Not implemented!")
