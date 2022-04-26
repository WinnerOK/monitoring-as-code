from typing import Collection, Iterable, Type

from binds.grafana.handlers.folder import FolderHandler
from binds.grafana.objects import Folder, GrafanaObject
from controller.diff_utils import RESOURCE_DIFF, calculate_diff
from controller.provider import Provider
from controller.resource import (
    LocalResource,
    MappedResource,
    ObsoleteResource,
    SyncedResource,
)
from controller.utils import get_resource_object_type_name
from requests import Session


class GrafanaProvider(Provider[GrafanaObject]):
    def __init__(
        self,
        http_session: Session,
    ):
        self.http_session = http_session

        self.handlers = {
            Folder: FolderHandler(http_session),
        }
        self.handlers_by_name = {
            obj_type.__name__: handler for obj_type, handler in self.handlers
        }

    @property
    def operating_objects(self) -> Collection[Type[GrafanaObject]]:
        return set(GrafanaObject.__subclasses__())

    def sync_resources(
        self, mapped_resources: Iterable[MappedResource[GrafanaObject]]
    ) -> Iterable[SyncedResource[GrafanaObject] | ObsoleteResource[GrafanaObject]]:
        return [self.handlers[type(r.local_object)].read(r) for r in mapped_resources]

    def diff(self, resource: SyncedResource[GrafanaObject]) -> RESOURCE_DIFF:
        return calculate_diff(resource.remote_object, resource.local_object)

    def apply_actions(
        self,
        to_create: Iterable[LocalResource[GrafanaObject]],
        to_update: Iterable[SyncedResource[GrafanaObject]],
        to_remove: Iterable[ObsoleteResource[GrafanaObject]],
    ) -> list[SyncedResource[GrafanaObject]]:
        # todo: somehow set order of processing to set up object dependencies
        created = [self.handlers[type(r.local_object)].create(r) for r in to_create]

        updated = [self.handlers[type(r.local_object)].update(r) for r in to_update]

        for r in to_remove:
            self.handlers_by_name[get_resource_object_type_name(r)].delete(r)

        return created + updated
