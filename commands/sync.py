import argparse
import os
from common import IceboxError
from common import IceboxStorageError
from common import utils

parser = argparse.ArgumentParser(description='Parse arguments for sync command.')
parser.add_argument('remote', type=str,
                    help='remote path to sync.', default=None)
parser.add_argument('local', type=str,
                    help='local path to sync.', default=None)

class IceboxSyncCommand:
    def __init__(self, args=[]):
        parsed_args = parser.parse_args(args)
        self.remote = parsed_args.remote
        self.local = utils.ResolvePath(parsed_args.local)
        self.icebox = utils.FindIcebox(self.local)
        self.storage = utils.GetStorage()

    def run(self):
        if not self.remote:
            raise IceboxError("Missing remote path!")
        if not self.local:
            raise IceboxError("Missing local path!")

        # check if we need to create a local directory
        if os.path.exists(self.local) and not os.path.isdir(self.local):
            raise IceboxError("Local path points to a file. Must be a directory.")
        elif not os.path.exists(self.local):
            # create local directory
            os.makedirs(self.local)

        # check if local is an existing icebox
        if self.icebox:
            raise IceboxError(f"'{self.local}' is an existing icebox! Cannot sync here.")

        print(f"Syncing '{self.remote}' to '{self.local}'...")
        utils.SyncIcebox(self.remote, self.local, storage=self.storage)
