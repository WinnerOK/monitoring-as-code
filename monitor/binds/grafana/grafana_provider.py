from typing import Type

from monitor.controller.resource import Resource
from monitor.controller.provider import Provider
from monitor.binds.grafana import resources as gf_resources


class GrafanaProvider(Provider):
    @property
    def operating_resources(self) -> set[Type[Resource]]:
        return {
            gf_resources.Folder,
        }

