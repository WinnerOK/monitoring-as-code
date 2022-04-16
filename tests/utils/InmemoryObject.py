from abc import ABC

from monitor.controller.obj import MonitoringObject


class InmemoryObject(MonitoringObject, ABC):
    name: str

    @property
    def local_id(self) -> str:
        return f"{type(self).__name__}.{self.name}"


class PrimitiveInmemoryObject(InmemoryObject):
    pass


class NestedPrimitiveInmemoryObject(InmemoryObject):
    str_list: list[str]


class NestedComposeInmemoryObject(InmemoryObject):
    str_list: list[PrimitiveInmemoryObject]
