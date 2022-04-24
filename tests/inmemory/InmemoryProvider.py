from typing import Collection, Iterable, Type

from monitor.controller.diff_utils import RESOURCE_DIFF, calculate_diff
from monitor.controller.provider import Provider
from monitor.controller.provider import T
from monitor.controller.resource import IdType
from monitor.controller.resource import (
    ObsoleteResource,
    SyncedResource,
    LocalResource,
    MappedResource,
)
from tests.inmemory.InmemoryObject import InmemoryObject


class InmemoryProvider(Provider[InmemoryObject]):
    @staticmethod
    def generate_remote_id(local_id: str) -> str:
        return "remote_" + local_id

    def __init__(self, remote_objects: Iterable[InmemoryObject]):
        self.remote_state: dict[IdType, InmemoryObject] = {
            self.generate_remote_id(LocalResource(local_object=obj).local_id): obj
            for obj in remote_objects
        }

    @property
    def operating_objects(self) -> Collection[Type[InmemoryObject]]:
        return set(InmemoryObject.__subclasses__())

    def sync_resources(
        self, mapped_resources: Iterable[MappedResource[T]]
    ) -> Iterable[SyncedResource[T] | ObsoleteResource[T]]:
        rv = []
        for resource in mapped_resources:
            remote_obj = self.remote_state.get(resource.remote_id)

            if remote_obj:
                rv.append(
                    SyncedResource(
                        local_object=resource.local_object,
                        remote_id=resource.remote_id,
                        remote_object=remote_obj,
                    )
                )
            else:
                rv.append(
                    ObsoleteResource(
                        local_id=resource.local_id,
                        remote_id=resource.remote_id,
                    )
                )
        return rv

    def diff(self, resource: SyncedResource[T]) -> RESOURCE_DIFF:
        return calculate_diff(resource.remote_object, resource.local_object)

    def apply_actions(
        self,
        to_create: Iterable[LocalResource[T]],
        to_update: Iterable[SyncedResource[T]],
        to_remove: Iterable[ObsoleteResource[T]],
    ) -> list[SyncedResource[T]]:
        synced = []

        for obsolete_resource in to_remove:
            self.remote_state.pop(
                obsolete_resource.remote_id
            )  # probably make default None

        for synced_resource in to_update:
            self.remote_state[synced_resource.remote_id] = synced_resource.local_object
            synced.append(synced_resource)

        for local_resource in to_create:
            remote_id = self.generate_remote_id(local_resource.local_id)

            self.remote_state[remote_id] = local_resource.local_object
            synced.append(
                SyncedResource(
                    local_object=local_resource.local_object,
                    remote_id=remote_id,
                    remote_object=local_resource.local_object,
                )
            )

        return synced
