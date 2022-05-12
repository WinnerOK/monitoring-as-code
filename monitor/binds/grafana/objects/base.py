from abc import ABC

from controller.obj import MonitoringObject

__all__ = [
    "GrafanaObject",
]


class GrafanaObject(MonitoringObject, ABC):
    pass

    # def json(
    #     self,
    #     *,
    #     by_alias: bool = True,
    #     **kwargs,
    # ) -> str:
    #     return super(GrafanaObject, self).json(by_alias=by_alias, **kwargs)
