from abc import ABC

from monitoring_as_code.controller.obj import MonitoringObject


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
    obj_list: list[PrimitiveInmemoryObject]
