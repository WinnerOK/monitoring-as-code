# Deprecated concept
from typing import Generic, TypeVar

from abc import ABC, abstractmethod

from monitor.controller.api_entity import ID_TYPE, ApiEntity

T = TypeVar("T", bound=ApiEntity)


class API(Generic[T], ABC):
    @abstractmethod
    def read(self, object_id: ID_TYPE) -> T:
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, object_id: ID_TYPE) -> None:
        pass
