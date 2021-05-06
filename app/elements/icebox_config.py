import pydantic
import typing

from app.storage.icebox_storage import IceboxStorageType


class IceboxConfig(pydantic.BaseModel):
    storage_choice: IceboxStorageType = None
    storage_options: typing.Dict[str, str] = None
