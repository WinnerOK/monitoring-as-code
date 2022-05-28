from typing import Generic, TypeVar

from abc import ABC, abstractmethod

from requests import Session

from .obj import MonitoringObject
from .resource import LocalResource, MappedResource, ObsoleteResource, SyncedResource

T = TypeVar("T", bound=MonitoringObject)


class ResourceHandler(Generic[T], ABC):
    @abstractmethod
    def read(
        self,
        resource: MappedResource[T],
    ) -> SyncedResource[T] | ObsoleteResource[T]:
        pass

    @abstractmethod
    def create(
        self,
        resource: LocalResource[T],
    ) -> SyncedResource[T]:
        pass

    @abstractmethod
    def update(
        self,
        resource: SyncedResource[T],
    ) -> SyncedResource[T]:
        pass

    @abstractmethod
    def delete(
        self,
        resource: ObsoleteResource[T],
    ) -> None:
        pass


class HttpApiResourceHandler(ResourceHandler[T], ABC):
    def __init__(self, client: Session):
        self.client = client
