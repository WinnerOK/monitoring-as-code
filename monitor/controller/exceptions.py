from typing import Iterable

from controller.obj import MonitoringObject
from monitor.controller.resource import Resource


class MonitorException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super(MonitorException, self).__init__(self.message)


class UnknownObjectHandlerException(MonitorException):
    def __init__(self, objects: list[MonitoringObject]) -> None:
        message = (
            "No handler is registered for the following object types: {types}".format(
                types={type(obj) for obj in objects}
            )
        )
        super(UnknownObjectHandlerException, self).__init__(message)


class DuplicatedProviderException(MonitorException):
    def __init__(self) -> None:
        message = "Some objects are handled by multiple providers"
        super(DuplicatedProviderException, self).__init__(message)


class UnexpectedResourceStateException(MonitorException):
    def __init__(self, resources: Iterable[Resource[MonitoringObject]]) -> None:
        message = f"Some resources ended up in an unexpected state: {resources}"
        super(UnexpectedResourceStateException, self).__init__(message)
