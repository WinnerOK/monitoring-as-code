from typing import Collection, Iterable, Type, TypeVar

from binds.grafana.handlers.alert import AlertHandler
from binds.grafana.handlers.folder import FolderHandler
from binds.grafana.objects import Folder, GrafanaObject
from binds.grafana.objects.alert import Alert
from binds.grafana.utils import group_resources
from controller.diff_utils import RESOURCE_DIFF, calculate_diff
from controller.handler import ResourceHandler
from controller.provider import Provider
from controller.resource import (
    LocalResource,
    MappedResource,
    ObsoleteResource,
    SyncedResource,
)
from requests import Session

T = TypeVar("T", bound=GrafanaObject)


class GrafanaProvider(Provider[GrafanaObject]):
    def __init__(
        self,
        http_session: Session,
    ):
        self.http_session = http_session
        self.http_session.headers["Content-type"] = "application/json"

        self.handlers = {
            Folder: FolderHandler(http_session),
            Alert: AlertHandler(http_session),
        }

    @property
    def operating_objects(self) -> Collection[Type[GrafanaObject]]:
        return set(GrafanaObject.__subclasses__())

    def sync_resources(
        self, mapped_resources: Iterable[MappedResource[GrafanaObject]]
    ) -> Iterable[SyncedResource[GrafanaObject] | LocalResource[GrafanaObject]]:
        return [self.handlers[type(r.local_object)].read(r) for r in mapped_resources]

    def diff(self, resource: SyncedResource[GrafanaObject]) -> RESOURCE_DIFF:
        exclude = dict()
        if isinstance(resource.local_object, Alert):
            exclude = {"grafana_alert": {"uid"}}

        return calculate_diff(
            resource.remote_object,
            resource.local_object,
            exclude,
        )

    def apply_actions(
        self,
        to_create: Iterable[LocalResource[GrafanaObject]],
        to_update: Iterable[SyncedResource[GrafanaObject]],
        to_remove: Iterable[ObsoleteResource[GrafanaObject]],
    ) -> list[SyncedResource[GrafanaObject]]:
        type_names_to_types = {
            type_class.__name__: type_class for type_class in self.handlers.keys()
        }
        synced: list[SyncedResource[GrafanaObject]] = []

        to_create_grouped = group_resources(to_create, type_names_to_types)
        to_update_grouped = group_resources(
            to_update,
            type_names_to_types,
        )
        to_remove_grouped = group_resources(to_remove, type_names_to_types)

        obj_type: T
        handler: ResourceHandler[T]
        for obj_type, handler in self.handlers.items():
            synced.extend(
                [
                    self.handlers[obj_type].create(r_c)
                    for r_c in to_create_grouped.get(obj_type, [])
                ]
            )

            synced.extend(
                [
                    self.handlers[obj_type].update(r_u)
                    for r_u in to_update_grouped.get(obj_type, [])
                ]
            )

        for obj_type, handler in reversed(self.handlers.items()):
            for r_d in to_remove_grouped.get(obj_type, []):
                self.handlers[obj_type].delete(r_d)

        return synced
