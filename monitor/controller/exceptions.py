from typing import Iterable

from .obj import MonitoringObject
from .resource import Resource
from .utils import get_resource_object_type_name


class MonitorException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super(MonitorException, self).__init__(self.message)


class UnknownResourceProviderException(MonitorException):
    def __init__(self, resources: list[Resource]) -> None:
        message = (
            "No provider is registered for the following object types: {types}".format(
                types={get_resource_object_type_name(r) for r in resources}
            )
        )
        super().__init__(message)


class UnknownResourceHandlerException(MonitorException):
    def __init__(self, resources: list[Resource]) -> None:
        message = (
            "No handler is registered for the following object types: {types}".format(
                types={get_resource_object_type_name(r) for r in resources}
            )
        )
        super().__init__(message)


class DuplicatedProviderException(MonitorException):
    def __init__(self) -> None:
        message = "Some objects are handled by multiple providers"
        super(DuplicatedProviderException, self).__init__(message)


class UnexpectedResourceStateException(MonitorException):
    def __init__(self, resources: Iterable[Resource[MonitoringObject]]) -> None:
        message = f"Some resources ended up in an unexpected state: {resources}"
        super(UnexpectedResourceStateException, self).__init__(message)
