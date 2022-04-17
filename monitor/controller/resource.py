from typing import Generic, Optional, TypeVar

from enum import Enum, auto

from pydantic import BaseModel

from monitor.controller.obj import MonitoringObject

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
    # fixme Type cannot be covariant, because resource accepts it
    # covariant=True,  # if A <: B, then Resource[A] <: Resource[B]
)


class Resource(Generic[T], BaseModel):
    local_object: T
    remote_id: Optional[IdType] = None
    remote_object: Optional[T] = None

    @property
    def local_id(self) -> IdType:
        return self.local_object.local_id


class ResourceAction(Generic[T], BaseModel):
    resource: Resource[T]
    operation: ResourceOps
