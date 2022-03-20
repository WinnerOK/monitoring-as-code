from enum import Enum, auto
from typing import Union

from pydantic import BaseModel


class ResourceOps(Enum):
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()

    SKIP = auto()

    @staticmethod
    def modifying_ops() -> set['ResourceOps']:
        # todo: check if obsolete
        return {
            ResourceOps.CREATE,
            ResourceOps.UPDATE,
            ResourceOps.DELETE,
        }


IdType = Union[str, int]


class Resource(BaseModel):
    _local_id: IdType
