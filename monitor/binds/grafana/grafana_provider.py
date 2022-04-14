from typing import Type

from monitor.binds.grafana import resources as gf_resources
from monitor.controller.provider import Provider
from monitor.controller.resource import Resource


class GrafanaProvider(Provider):
    @property
    def operating_resources(self) -> set[Type[Resource]]:
        return {
            Resource[gf_resources.Folder],
        }
