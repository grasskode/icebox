import argparse
from datetime import datetime
from typing import Optional
from common import IceboxError
from common import IceboxStorageError
from common import utils

TIME_FORMAT = "%d %b %Y %H:%M"

parser = argparse.ArgumentParser(description='Parse arguments for list command.')
parser.add_argument('remote', type=str,
                    help='remote path to list.', default=None)
parser.add_argument('-r', dest='recursive', action='store_true',
                    help='list recursively.')

class IceboxListCommand:
    def __init__(self, args=[]):
        parsed_args = parser.parse_args(args)
        self.remote = parsed_args.remote
        self.recursive = parsed_args.recursive
        self.storage = utils.GetStorage()

    def run(self):
        if not self.remote:
            raise IceboxError("Missing remote path!")
        print(f"Listing '{self.remote}'...")
        try:
            dirs, files = self.storage.List(self.remote, recursive=self.recursive)
            total_items = len(dirs)+len(files)
            print(f"{total_items} items found.")
            if total_items > 0:
                max_size_width = len(str(max([lf['size'] for lf in files]))) if len(files) > 0 else 1
                max_time_width = len(datetime.now().strftime(TIME_FORMAT))
                # TODO possibly make the entire listing format configurable
                # TODO make the time format configurable
                for d in dirs:
                    print(f"{'':{max_size_width}} - {'':{max_time_width}} - {d}")
                for lf in files:
                    updated = lf['updated'].strftime(TIME_FORMAT)
                    print(f"{lf['size']:{max_size_width}} - {updated} - {lf['name']}")
        except IceboxStorageError as e:
            print(e)
            print(f"Unable to list {self.remote}! Check stack trace for error.")
