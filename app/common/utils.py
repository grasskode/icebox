import json
import os
from pathlib import Path
from typing import Optional

from .icebox_elements import Icebox
from .icebox_elements import IceboxConfig
from .exceptions import IceboxError

from app import config
from app.storage import google_cloud_storage as gcs
from app.storage import local_storage


def ResolveIcebox(icebox_path: Path) -> Path:
    if not icebox_path:
        return None
    return icebox_path / Path(config.ICEBOX_FILE_NAME)


def ResolvePath(path: str) -> Path:
    if not path:
        return None
    return Path(path).expanduser().resolve()


def ReadConfig() -> IceboxConfig:
    """Read config from the user home.

    Returns None if config file does not exit.
    """
    fn = (f"{config.ICEBOX_CONFIG_LOCATION}{os.sep}"
          f"{config.ICEBOX_CONFIG_FILE_NAME}")
    if not os.path.isfile(fn):
        # print("Config file not found!")
        return None
    with open(fn, 'r') as f:
        return IceboxConfig.from_dict(json.loads(f.read()))


def WriteConfig(config: IceboxConfig):
    """Write config to the user home."""
    filename = (f"{config.ICEBOX_CONFIG_LOCATION}{os.sep}"
                f"{config.ICEBOX_CONFIG_FILE_NAME}")
    print("Writing config.")
    with open(filename, 'w') as f:
        f.write(json.dumps(config.to_dict()))


def GetStorage():
    """Get the configured storage."""
    icebox_config = ReadConfig()
    if not icebox_config:
        if not config.IsTest():
            raise IceboxError("Icebox not configured.")
        else:
            # return local storage for test environment
            return local_storage.LocalStorage(config.LOCAL_STORAGE_PATH)
    if icebox_config.storage_choice == 'GCP':
        return gcs.GoogleCloudStorage(
            icebox_config.storage_options['credentials'],
            icebox_config.storage_options['default_location'],
            icebox_config.storage_options['bucket'])
    else:
        raise IceboxError(
            f"Invalid storage choice '{icebox_config.storage_choice}'!")


def SyncIcebox(remote: str, local: str, storage=None):
    if not storage:
        storage = GetStorage()
    # check if remote points to a valid icebox
    _, files = storage.List(remote)
    file_names = [file['name'] for file in files]
    if config.ICEBOX_FILE_NAME not in file_names:
        raise IceboxError(f"Invalid remote path '{remote}'.")
    # local points to a non initialized folder\
    # download remote config.ICEBOX_FILE_NAME to local
    remote_path = (f"{remote}{config.REMOTE_PATH_DELIMITER}"
                   f"{config.ICEBOX_FILE_NAME}")
    icebox_path = ResolveIcebox(local)
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


def FindIcebox(path: Path) -> Icebox:
    if not path:
        return None
    icebox_path = None
    while True:
        possible_icebox_path = ResolveIcebox(path)
        if possible_icebox_path.is_file():
            icebox_path = possible_icebox_path
            break
        elif path.parent == path:
            break
        else:
            path = path.parent
    if not icebox_path:
        return None
    with open(icebox_path, 'r') as f:
        return Icebox.from_dict(str(path), json.loads(f.read()))


def ExistsInIcebox(path: Path, icebox: Icebox) -> bool:
    relpath = GetRelativeRemotePath(str(path), icebox.path)
    if relpath:
        for f in icebox.frozen_files:
            if f.startswith(relpath):
                return True
    return False


def Finalize(icebox: Icebox):
    if not icebox:
        raise IceboxError("Cannot finalize without icebox!")
    icebox_path = ResolveIcebox(icebox.path)
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
    # TODO: we should copy the os.stat stuff to allow for same local browsing
    # experience.
    open(filepath, 'w').close()


def GetRelativeRemotePath(filepath: str, parentpath: str) -> Optional[str]:
    relpath = os.path.relpath(filepath, parentpath)
    if relpath.startswith('..'):
        return None
    else:
        return relpath.replace(os.sep, config.REMOTE_PATH_DELIMITER)


def GetAbsoluteLocalPath(relpath: str, parentpath: str) -> Path:
    return Path(parentpath) / Path(relpath)


def UploadFile(icebox: Icebox, filepath: str, storage=None):
    if not storage:
        storage = GetStorage()
    relative_path = GetRelativeRemotePath(filepath, icebox.path)
    dest_path = f"{icebox.id}{config.REMOTE_PATH_DELIMITER}{relative_path}"
    storage.Upload(filepath, dest_path)


def DownloadFile(icebox: Icebox, relative_path: str, storage=None):
    if not storage:
        storage = GetStorage()
    filepath = GetAbsoluteLocalPath(relative_path, icebox.path)
    remote_path = f"{icebox.id}{config.REMOTE_PATH_DELIMITER}{relative_path}"
    storage.Download(remote_path, filepath)
