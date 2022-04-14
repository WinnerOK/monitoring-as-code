from abc import ABC, abstractmethod
from typing import Collection, Generic, Iterable, Type, TypeVar

from monitor.controller.resource import Resource, ResourceAction

from .diff_utils import RESOURCE_DIFF
from .handler import ResourceHandler
from .obj import MonitoringObject

T = TypeVar("T", bound=MonitoringObject)


class Provider(ABC, Generic[T]):
    """
    An abstract class that represents a service provider
    The class exposes types it operates with and responsible for CRUD operations
    """

    @abstractmethod
    @property
    def operating_objects(self) -> Collection[Type[T]]:
        pass

    @abstractmethod
    @property
    def handlers(self) -> Iterable[ResourceHandler[T]]:
        pass

    @abstractmethod
    def sync_resources(
        self,
        local_resources: Iterable[Resource[T]],
    ) -> Iterable[Resource[T]]:
        """
        Get remote state for given resources, if any
        :param local_resources:
        :return:
        """

    @abstractmethod
    def diff(self, resource: Resource[T]) -> RESOURCE_DIFF:
        """
        Diff in form of classic diff

        see: https://docs.python.org/3/library/difflib.html#difflib.unified_diff
        """

    @abstractmethod
    def apply_actions(
        self,
        resource_actions: Iterable[ResourceAction],
    ) -> None:
        pass

    def dispose(self) -> None:
        """
        In case needed, run any finalizing actions
        """
