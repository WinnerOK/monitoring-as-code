from typing import Generic, TypeVar

from abc import ABC
from enum import Enum, auto

from pydantic import BaseModel

from .obj import MonitoringObject

IdType = str


class ResourceOps(Enum):
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()

    SKIP = auto()
    IGNORE = auto()

    @staticmethod
    def modifying_ops() -> set["ResourceOps"]:
        # todo: check if obsolete
        return {
            ResourceOps.CREATE,
            ResourceOps.UPDATE,
            ResourceOps.DELETE,
        }


T = TypeVar(
    "T",
    bound=MonitoringObject,
)


def generate_resource_local_id(obj: MonitoringObject) -> str:
    return f"{type(obj).__name__}.{obj.local_id}"


class Resource(BaseModel, Generic[T], ABC):
    pass


class LocalResource(Resource[T]):
    local_object: T

    @property
    def local_id(self) -> IdType:
        return generate_resource_local_id(self.local_object)


class MappedResource(LocalResource[T]):
    remote_id: IdType

    @classmethod
    def from_local(
        cls, local_resource: LocalResource[T], remote_id: IdType
    ) -> "MappedResource[T]":
        return cls(
            local_object=local_resource.local_object,
            remote_id=remote_id,
        )


class SyncedResource(MappedResource[T]):
    remote_object: T


class ObsoleteResource(Resource[T]):
    local_id: IdType
    remote_id: IdType
