from typing import Type

from monitor.binds.grafana import resources as gf_resources
from controller.provider import Provider
from controller.resource import Resource


class GrafanaProvider(Provider):
    @property
    def operating_resources(self) -> set[Type[Resource]]:
        return {
            Resource[gf_resources.Folder],
        }
