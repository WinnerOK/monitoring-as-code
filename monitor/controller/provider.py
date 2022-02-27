from abc import ABC, abstractmethod
from typing import Type

from monitor.controller.resource import Resource


class Provider(ABC):
    """
    An abstract class that represents a service provider
    The class exposes types it operates with and responsible for CRUD operations
    """
    @abstractmethod
    @property
    def operating_resources(self) -> set[Type[Resource]]:
        pass
