from typing import Collection, Generic, Iterable, Type, TypeVar

from abc import ABC, abstractmethod

from .diff_utils import RESOURCE_DIFF
from .obj import MonitoringObject
from .resource import LocalResource, MappedResource, ObsoleteResource, SyncedResource

T = TypeVar("T", bound=MonitoringObject)


class Provider(ABC, Generic[T]):
    """
    An abstract class that represents a service provider
    The class exposes types it operates with and responsible for CRUD operations
    """

    @property
    @abstractmethod
    def operating_objects(self) -> Collection[Type[T]]:
        pass

    @abstractmethod
    def sync_resources(
        self,
        mapped_resources: Iterable[MappedResource[T]],
    ) -> Iterable[SyncedResource[T] | LocalResource[T]]:
        """
        Get remote state for given resources, if any
        """

    @abstractmethod
    def diff(self, resource: SyncedResource[T]) -> RESOURCE_DIFF:
        """
        Diff in form of classic diff

        see: https://docs.python.org/3/library/difflib.html#difflib.unified_diff
        """

    @abstractmethod
    def apply_actions(
        self,
        to_create: Iterable[LocalResource[T]],
        to_update: Iterable[SyncedResource[T]],
        to_remove: Iterable[ObsoleteResource[T]],
    ) -> list[SyncedResource[T]]:
        pass

    def dispose(self) -> None:
        """
        In case needed, run any finalizing actions
        """
