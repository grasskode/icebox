import json
import os
import time
from pathlib import Path
from typing import Dict
from typing import Optional
from .icebox_elements import Icebox
from .icebox_elements import IceboxConfig
from coolname import generate_slug
from .exceptions import IceboxError
from storage import GoogleCloudStorage
from storage import GoogleCloudStorageError

CONFIG_FILE_NAME: str = ".iceboxcfg"
ICEBOX_FILE_NAME: str = ".icebox"
REMOTE_PATH_DELIMITER: str = "/"

def _icebox_file_path(icebox_path: str) -> str:
    return f"{icebox_path}{os.sep}{ICEBOX_FILE_NAME}"

def ResolvePath(path: str) -> str:
    if not path:
        return None
    p = Path(path).expanduser().resolve()
    return str(p)

def ReadConfig() -> IceboxConfig:
    """Read config from the user home. Return None if config file does not exit."""
    fn = f"{Path.home()}{os.sep}{CONFIG_FILE_NAME}"
    if not os.path.isfile(fn):
        print(f"Config file not found!")
        return None
    with open(fn, 'r') as f:
        return IceboxConfig.from_dict(json.loads(f.read()))

def WriteConfig(config: IceboxConfig):
    """Write config to the user home."""
    filename = f"{Path.home()}{os.sep}{CONFIG_FILE_NAME}"
    print(f"Writing config.")
    with open(filename, 'w') as f:
        f.write(json.dumps(config.to_dict()))

def GetStorage():
    """Get the configured storage."""
    icebox_config = ReadConfig()
    if icebox_config.storage_choice == 'GCP':
        return GoogleCloudStorage(icebox_config.storage_options['credentials'], icebox_config.storage_options['default_location'], icebox_config.storage_options['bucket'])
    else:
        raise IceboxError(f"Invalid storage choice '{icebox_config.storage_choice}'!")

def SyncIcebox(remote: str, local: str, storage = None):
    if not storage:
        storage = GetStorage()
    # check if remote points to a valid icebox
    _, files = storage.List(remote)
    file_names = [file['name'] for file in files]
    if ICEBOX_FILE_NAME not in file_names:
        raise IceboxError(f"Invalid remote path '{remote}'.")
    # local points to a non initialized folder\
    # download remote ICEBOX_FILE_NAME to local
    remote_path = f"{remote}{REMOTE_PATH_DELIMITER}{ICEBOX_FILE_NAME}"
    icebox_path = _icebox_file_path(local)
    storage.Download(remote_path, icebox_path)
    icebox = FindIcebox(local)
    for f in icebox.frozen_files:
        # create a local replica for all frozen files
        filepath = f"{icebox.path}{os.sep}{f}"
        dirpath = os.path.dirname(filepath)
        print(filepath, dirpath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        ReplaceFile(filepath)

def CreateIcebox(path: str):
    icebox_path = _icebox_file_path(path)
    # raise error if icebox already exists
    if os.path.isfile(icebox_path):
        raise IceboxError(f"Cannot create icebox. Another already exists at '{icebox_path}'.")
    # use the path to initialize an icebox
    icebox = Icebox(f"{generate_slug(2)}_{int(time.time())}", path)
    with open(icebox_path, 'w') as f:
        f.write(json.dumps(icebox.to_dict()))
    try:
        UploadFile(icebox, icebox_path)
    except Exception as e:
        # remove icebox file if there was an error uploading
        os.remove(icebox_path)
        raise e

def FindIcebox(path: str) -> Icebox:
    p = Path(path)
    icebox_path = None
    while True:
        possible_icebox_path = _icebox_file_path(str(p))
        if os.path.isfile(possible_icebox_path):
            icebox_path = possible_icebox_path
            break
        elif p.parent == p:
            break
        else:
            p = p.parent
    if not icebox_path:
        return None
    with open(icebox_path, 'r') as f:
        return Icebox.from_dict(str(p), json.loads(f.read()))

def Finalize(icebox: Icebox):
    if not icebox:
        raise IceboxError("Cannot finalize without icebox!")
    icebox_path = _icebox_file_path(icebox.path)
    with open(icebox_path, 'w') as f:
        f.write(json.dumps(icebox.to_dict()))
    # upload icebox to remote
    UploadFile(icebox, icebox_path)

def ReplaceFile(filepath: str):
    """Replace the given filepath with a preview or metadata file."""
    # remove file if it exists
    if os.path.exists(filepath) and os.path.isfile(filepath):
        os.remove(filepath)
    # try to create a blank file
    ## TODO: we should copy the os.stat stuff to allow for same local browsing experience.
    open(filepath, 'w').close()

def GetRelativePath(filepath: str, icebox: Icebox) -> Optional[str]:
    relpath = os.path.relpath(filepath, icebox.path)
    if relpath.startswith('..'):
        return None
    else:
        return relpath.replace(os.sep, REMOTE_PATH_DELIMITER)

def UploadFile(icebox: Icebox, filepath: str, storage = None):
    if not storage:
        storage = GetStorage()
    relative_path = GetRelativePath(filepath, icebox)
    dest_path = f"{icebox.id}{REMOTE_PATH_DELIMITER}{relative_path}"
    storage.Upload(filepath, dest_path)

def DownloadFile(icebox: Icebox, filepath: str, storage = None):
    if not storage:
        storage = GetStorage()
    relative_path = GetRelativePath(filepath, icebox)
    remote_path = f"{icebox.id}{REMOTE_PATH_DELIMITER}{relative_path}"
    storage.Download(remote_path, filepath)
