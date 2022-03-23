from abc import ABC, abstractmethod
from typing import Type, List, TypeVar, Generic

from monitor.controller.resource import Resource
from .handler import ResourceHandler

T = TypeVar("T", bound=Resource)


class Provider(ABC, Generic[T]):
    """
    An abstract class that represents a service provider
    The class exposes types it operates with and responsible for CRUD operations
    """
    @abstractmethod
    @property
    def operating_resources(self) -> List[Type[T]]:
        pass

    @abstractmethod
    @property
    def handlers(self) -> List[ResourceHandler[T]]:
        pass

    def process_resources(self, resources: List[T], dry_run: bool = True):
        pass
