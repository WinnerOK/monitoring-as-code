from abc import ABC

from controller.obj import MonitoringObject

__all__ = [
    "GrafanaObject",
]


class GrafanaObject(MonitoringObject, ABC):
    pass
