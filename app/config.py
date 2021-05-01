import os
from pathlib import Path

ICEBOX_CONFIG_LOCATION: str = os.environ.get('ICEBOX_CONFIG_LOCATION',
                                             Path.home())
ICEBOX_CONFIG_FILE_NAME: str = os.environ.get('ICEBOX_CONFIG_FILE_NAME',
                                              ".iceboxcfg")
ICEBOX_FILE_NAME: str = os.environ.get('ICEBOX_FILE_NAME', ".icebox")
REMOTE_PATH_DELIMITER: str = "/"
LOCAL_STORAGE_PATH: str = os.environ.get('LOCAL_STORAGE_PATH')
ICEBOX_TIME_FORMAT: str = os.environ.get('ICEBOX_TIME_FORMAT',
                                         "%d %b %Y %H:%M")


def IsTest() -> bool:
    return os.environ.get('ICEBOX_ENV', "").lower() == "test"
