from typing import Generic, TypeVar

from abc import ABC

from pydantic import BaseModel

from monitor.controller.obj import MonitoringObject

T = TypeVar("T", bound=MonitoringObject)


class SomeFoo(MonitoringObject):
    @property
    def local_id(self) -> str:
        return "123"


class Base(BaseModel, Generic[T], ABC):
    pass


class Model(Base[T]):
    foo: T


f = Model(foo=SomeFoo())

a = 3
