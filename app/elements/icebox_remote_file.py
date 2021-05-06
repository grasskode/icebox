import pydantic

from datetime import datetime


class IceboxRemoteFile(pydantic.BaseModel):
    name: str
    size: int = 0
    updated: datetime = 0
    is_dir: bool = False
