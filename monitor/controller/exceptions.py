from typing import Iterable, List

from monitor.controller import Resource


class MonitorException(Exception):
    def __init__(self, message: str):
        self.message = message
        super(MonitorException, self).__init__(self.message)


class UnknownObjectHandlerException(MonitorException):
    def __init__(self, resources: List[Resource]):
        message = (
            "No handler is registered for the following object types: {types}".format(
                types={type(resource) for resource in resources}
            )
        )
        super(UnknownObjectHandlerException, self).__init__(message)


class DuplicatedProviderException(MonitorException):
    def __init__(self):
        message = "Some objects are handled by multiple providers"
        super(DuplicatedProviderException, self).__init__(message)


class UnexpectedResourceStateException(MonitorException):
    def __init__(self, resources: Iterable[Resource]):
        message = f"Some resources ended up in an unexpected state: {resources}"
        super(UnexpectedResourceStateException, self).__init__(message)
