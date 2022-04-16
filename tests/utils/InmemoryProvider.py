from typing import Collection, Iterable, Type

from monitor.controller.diff_utils import RESOURCE_DIFF, calculate_diff
from monitor.controller.provider import Provider
from monitor.controller.resource import IdType, Resource, ResourceAction, ResourceOps
from tests.utils.InmemoryObject import InmemoryObject


class InmemoryProvider(Provider[InmemoryObject]):
    def __init__(self, remote_objects: Iterable[InmemoryObject]):
        self.remote_state: dict[IdType, InmemoryObject] = {
            self.generate_remote_id(obj.local_id): obj for obj in remote_objects
        }

    @staticmethod
    def generate_remote_id(local_id: str) -> str:
        return "remote_" + local_id

    @property
    def operating_objects(self) -> Collection[Type[InmemoryObject]]:
        return set(InmemoryObject.__subclasses__())

    def sync_resources(
        self, local_resources: Iterable[Resource[InmemoryObject]]
    ) -> Iterable[Resource[InmemoryObject]]:
        for resource in local_resources:
            if resource.remote_id is not None:
                resource.remote_object = self.remote_state.get(resource.remote_id, None)
        return local_resources

    def diff(self, resource: Resource[InmemoryObject]) -> RESOURCE_DIFF:
        return calculate_diff(resource.remote_object, resource.local_object)

    def apply_actions(self, resource_actions: Iterable[ResourceAction]) -> None:
        for resource_action in resource_actions:
            resource = resource_action.resource
            operation = resource_action.operation

            if operation == ResourceOps.CREATE:
                resource.remote_id = self.generate_remote_id(resource.local_id)

            if operation in {ResourceOps.CREATE, ResourceOps.UPDATE}:
                assert resource.remote_id is not None
                resource.remote_object = resource.local_object.copy(deep=True)

                self.remote_state[resource.remote_id] = resource.remote_object

            elif operation == ResourceOps.DELETE:
                self.remote_state.pop(resource.remote_id)
            elif operation in {ResourceOps.SKIP, ResourceOps.IGNORE}:
                pass
            else:
                raise RuntimeError(f"Unhandled operation: {operation}")
