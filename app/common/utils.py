import json
import os
import shutil
import typing

from pathlib import Path
from typing import Optional

from app import config
from app.elements.icebox import Icebox
from app.elements.icebox import IceboxError
from app.elements.icebox import LocalIcebox
from app.elements.icebox_config import IceboxConfig
from app.storage import google_cloud_storage as gcs
from app.storage import icebox_storage
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
        config_json = json.loads(f.read())
    return IceboxConfig(**config_json)


def WriteConfig(iceboxcfg: IceboxConfig):
    """Write config to the user home."""
    filename = (f"{config.ICEBOX_CONFIG_LOCATION}{os.sep}"
                f"{config.ICEBOX_CONFIG_FILE_NAME}")
    # ensure that the parent folder exists.
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    print("Writing config.")
    config_json = json.dumps(iceboxcfg.dict())
    with open(filename, 'w') as f:
        f.write(config_json)


def GetStorage():
    """Get the configured storage."""
    if config.IsTest():
        # return local storage for test environment
        return local_storage.LocalStorage(config.LOCAL_STORAGE_PATH)

    # for non-test, read configuration and return the appropriate storage.
    icebox_config = ReadConfig()
    if not icebox_config:
        raise IceboxError("Icebox not configured.")

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


def FindIcebox(path: Path) -> typing.Optional[LocalIcebox]:
    if not path:
        return None
    while True:
        # try to read icebox in current path and return if one was found
        icebox = ReadIcebox(path)
        if icebox:
            return LocalIcebox(path=str(path), **(icebox.dict()))
        elif path.parent == path:
            # icebox does not exist if we have reached the end of
            # upward iteration.
            return None
        else:
            # try looking for icebox in the parent
            path = path.parent


def ReadIcebox(path: Path) -> typing.Optional[Icebox]:
    if not path:
        return None
    icebox_path = ResolveIcebox(path)
    if icebox_path.is_file():
        with open(icebox_path, 'r') as f:
            return Icebox(**json.loads(f.read()))
    return None


def ExistsInIcebox(path: Path, icebox: LocalIcebox) -> bool:
    relpath = GetRelativeRemotePath(str(path), icebox.path)
    if relpath:
        for f in icebox.frozen_files:
            if f.startswith(relpath):
                return True
    return False


def Finalize(icebox: LocalIcebox):
    """Finalize an icebox.

    Write out the icebox locally and upload it to the configured remote.

    Raises:
        IceboxError
        IceboxStorageError
    """
    if not icebox:
        raise IceboxError("Cannot finalize without icebox!")
    icebox_path = ResolveIcebox(icebox.path)
    # write the icebox file locally
    with open(icebox_path, 'w') as f:
        data = Icebox(**icebox.dict()).dict()
        f.write(json.dumps(data))
    try:
        # upload icebox to remote
        UploadFile(icebox, icebox_path)
    except icebox_storage.IceboxStorageError as e:
        icebox_path.unlink(missing_ok=True)
        raise e

def Synchronize(icebox: LocalIcebox) -> LocalIcebox:
    if not icebox:
        raise IceboxError("Cannot synchronize without icebox!")
    temp_file_name = f"{config.ICEBOX_FILE_NAME}_temp"
    DownloadFile(
        icebox, config.ICEBOX_FILE_NAME,
        relative_destination_path=temp_file_name)
    temp_file_path = Path(icebox.path) / Path(temp_file_name)
    try:
        with open(temp_file_path, 'r') as f:
            remote_icebox = Icebox(**json.loads(f.read()))
        local_icebox = LocalIcebox(
            path=icebox.path, **remote_icebox.dict())
        if not local_icebox.is_valid():
            raise IceboxError("Invalid icebox found in remote location!")
    except Exception:
        # delete the temporary file
        temp_file_path.unlink(missing_ok=True)
        raise IceboxError(
            "Error reading remote icebox. Contents might be invalid.")
    else:
        shutil.copyfile(
            str(temp_file_path),
            f"{icebox.path}{os.sep}{config.ICEBOX_FILE_NAME}")
    # delete the temporary file
    temp_file_path.unlink(missing_ok=True)
    return local_icebox


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


def UploadFile(icebox: LocalIcebox, filepath: str, storage=None):
    if not storage:
        storage = GetStorage()
    relative_path = GetRelativeRemotePath(filepath, icebox.path)
    dest_path = f"{icebox.id}{config.REMOTE_PATH_DELIMITER}{relative_path}"
    storage.Upload(filepath, dest_path)


def DownloadFile(
        icebox: LocalIcebox, relative_path: str,
        relative_destination_path: str = None, storage=None):
    if not storage:
        storage = GetStorage()
    filepath = GetAbsoluteLocalPath(
        relative_path if not relative_destination_path
        else relative_destination_path,
        icebox.path)
    remote_path = f"{icebox.id}{config.REMOTE_PATH_DELIMITER}{relative_path}"
    storage.Download(remote_path, filepath)
