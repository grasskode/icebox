from typing import Dict
from typing import List

class IceboxConfig:
    def __init__(self, storage_choice: str = None, storage_options: Dict[str, str] = None):
        self.storage_choice = storage_choice
        self.storage_options = storage_options

    def to_dict(self):
        return {
            'storage_choice': self.storage_choice,
            'storage_options': self.storage_options
        }

    @classmethod
    def from_dict(cls, dict):
        return IceboxConfig(dict['storage_choice'], dict['storage_options'])


class Icebox:
    def __init__(self, id: str, path: str, frozen_files: List[str] = []):
        ## TODO: Every Icebox should have a unique identifier (possibly human readable). This path will be machine dependant and should not be used. Ideally a remote icebox should map to a local path and this information should be stored within the machine.
        # Think of adding this to the init process. Whenever an icebox is init, it is assigned an id. The local .icebox file created contains the path (or might not need to) and the remote simply contains the ID.
        # Adding path to .icebox makes us sure that moving the file around would not affect operations.
        # Also think about inconsistencies like frozen file deleted from local (should be deleted from remote?). Possibly push and pull functionalities. Ormaybe sync can do this as well. If the remote and local are already configured, it simply gets the information in a consistent state.
        self.id = id
        self.path = path
        ## TODO: frozen_files should be a set
        ## TODO: files should contain more than a simple list of path. Perhaps metadata and a date of freeze.
        self.frozen_files = frozen_files

    def to_dict(self):
        return {
            'id': self.id,
            'frozen_files': self.frozen_files
        }

    @classmethod
    def from_dict(cls, path, dict):
        return Icebox(id=dict['id'], path=path, frozen_files=dict.get('frozen_files'))
