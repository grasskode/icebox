import os
from common import utils
from common import IceboxConfig
from common import IceboxError
from storage import GoogleCloudStorage
from typing import Dict
from coolname import generate_slug

class IceboxConfigCommand:
    def __init__(self):
        self.config = utils.ReadConfig()

    def run(self):
        # check if config file already exists
        if not self.config:
            self.config = IceboxConfig()
        # get storage choice if it does not exist
        if not self.config.storage_choice:
            storage_choice = self._get_storage_choice()
            if storage_choice == 1:
                self.config.storage_choice = 'GCP'
            elif storage_choice == 2:
                self.config.storage_choice = 'AWS'
            else:
                raise IceboxError("Unknown storage choice!")
        # configure the storage
        if self.config.storage_choice == 'GCP':
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

    def _get_storage_choice(self) -> int :
        storage_choice = 0
        while storage_choice not in range(1,3):
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
        return storage_choice

    def _create_gcp_config(self) -> Dict[str, str]:
        """Store GCP credentials in the icebox config file."""
        print("Enter path for the GCP service account credentials:", end=" ")
        cred = utils.ResolvePath(str(input()))
        if not os.path.isfile(cred):
            raise IceboxError("File does not exist at mentioned path.")
        location = "asia-south1"
        print(f"Enter preferred GCP location (https://cloud.google.com/storage/docs/locations) [{location}]:", end=" ")
        input_location = input().strip()
        if input_location != '':
            location = input_location
        bucket_name = generate_slug(4)
        print(f"Enter a unique bucket name. Leave blank to use auto generated name ({bucket_name}):", end=" ")
        input_bucket_name = input().strip()
        if input_bucket_name != '':
            bucket_name = input_bucket_name
        # prepend `icebox_` to identify that it is an icebox bucket
        bucket_name = f"icebox_{bucket_name}"
        # Attempt to create storage client using the given credentials
        print("Checking access permissions.")
        storage = GoogleCloudStorage(cred, location, bucket_name)
        return {
            'bucket': bucket_name,
            'credentials': cred,
            'default_location': location
        }

    def _configure_gcp(self, storage_config: Dict[str, str]):
        GoogleCloudStorage(storage_config['credentials'], storage_config['default_location'], storage_config['bucket'])

    def _create_aws_config(self):
        raise IceboxError("Not implemented!")

    def _configure_aws(self, storage_config: Dict[str, str]):
        raise IceboxError("Not implemented!")
