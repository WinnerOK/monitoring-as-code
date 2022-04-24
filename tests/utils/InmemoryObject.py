from abc import ABC

from monitor.controller.obj import MonitoringObject


class InmemoryObject(MonitoringObject, ABC):
    key: str

    @property
    def local_id(self) -> str:
        return f"{self.key}"


class PrimitiveInmemoryObject(InmemoryObject):
    name: str


class NestedPrimitiveInmemoryObject(InmemoryObject):
    str_list: list[str]


class NestedComposeInmemoryObject(InmemoryObject):
    str_list: list[PrimitiveInmemoryObject]
