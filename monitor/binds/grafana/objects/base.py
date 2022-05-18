from abc import ABC

from controller.obj import MonitoringObject

__all__ = [
    "GrafanaObject",
]


class GrafanaObject(MonitoringObject, ABC):
    def json(
        self,
        *,
        by_alias: bool = True,
        models_as_dict: bool = False,
        **kwargs,
    ) -> str:
        return super(GrafanaObject, self).json(
            by_alias=by_alias,
            models_as_dict=models_as_dict,
            **kwargs,
        )
