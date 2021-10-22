from pathlib import Path
import pydantic

from datetime import datetime


class IceboxRemoteFile(pydantic.BaseModel):
    name: str
    size: int = 0
    updated: datetime = 0
    is_dir: bool = False

    @classmethod
    def from_path(cls, name: str, path: Path):
        if path.is_dir():
            return IceboxRemoteFile(
                name=name, is_dir=True)
        else:
            return IceboxRemoteFile(
                name=name, size=path.stat().st_size,
                updated=datetime.fromtimestamp(path.stat().st_mtime))
