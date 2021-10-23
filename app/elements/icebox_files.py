from pathlib import Path
import pydantic

from datetime import datetime


class IceboxRemoteFile(pydantic.BaseModel):
    name: str
    size: int = 0
    updated: datetime = 0
    is_dir: bool = False


class IceboxLocalFile(pydantic.BaseModel):
    name: str
    size: int = 0
    updated: datetime = 0
    is_dir: bool = False
    is_frozen: bool = False
    is_modified: bool = False

