from typing import List

from monitor.controller import Resource


class MonitorException(Exception):
    def __init__(self, message: str):
        self.message = message
        super(MonitorException, self).__init__(self.message)


class UnknownResourceHandler(MonitorException):
    def __init__(self, resources: List[Resource]):
        message = "No handler is registered for the following resource types: {types}".format(
            types={type(resource) for resource in resources}
        )
        super(UnknownResourceHandler, self).__init__(message)
