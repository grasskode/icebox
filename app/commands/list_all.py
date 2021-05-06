import os

from app.common import utils
from app.storage.icebox_storage import IceboxStorage


class IceboxListAllCommand:
    def __init__(self):
        self.storage: IceboxStorage = utils.GetStorage()

    def run(self):
        # no checks required
        iceboxes = self.list_all()
        for i in iceboxes:
            print(f"{i.id}{os.sep}")

    def list_all(self):
        """Utility function to enable testing."""
        return self.storage.ListAll()
