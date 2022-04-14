from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Optional, Type, Iterable

from pydantic import BaseModel

from controller.resource import IdType, Resource, ResourceAction, ResourceOps

RESOURCE_ID_MAPPING = dict[IdType, IdType]  # local_id: remote_id


class StateData(BaseModel):
    resources: RESOURCE_ID_MAPPING = {}


class State(ABC):
    def __init__(
        self,
        save_state: bool,
        persist_untracked: bool,
    ):
        self._data: StateData = StateData()
        self._persist_untracked = persist_untracked
        self._save_state = save_state

    @abstractmethod
    def _load(self) -> None:
        """
        Load state information to self._data
        """
        pass

    @abstractmethod
    def _save(self):
        """
        Persist self._data
        Do not consider self._save_stave; It is already handled in self.__exit__
        """
        pass

    def fill_provider_id(self, resources: Iterable[Resource]) -> None:
        for resource in resources:
            if (local_id := resource.local_id) in self._data.resources:
                resource.remote_id = self._data.resources[local_id]

    def filter_untracked_resources(
        self, resources: Iterable[Resource]
    ) -> RESOURCE_ID_MAPPING:
        """
        Return list of resources that are in state, but were not passed as parameters
        """
        if not self._persist_untracked:
            return {}

        tracked_resource_local_ids = {
            tracked_resource.local_id for tracked_resource in resources
        }
        untracked_storage = {
            local_id: remote_id
            for local_id, remote_id in self._data.resources.values()
            if local_id not in tracked_resource_local_ids
        }
        return untracked_storage

    def update_state(self, resource_actions: Iterable[ResourceAction]):
        for resource_action in resource_actions:
            resource = resource_action.resource
            operation = resource_action.operation

            if operation in {ResourceOps.DELETE, ResourceOps.IGNORE}:
                self._data.resources.pop(resource.local_id, None)
            # todo: this resources must always have remote_id set, but better to ensure it at type level
            elif operation in {ResourceOps.CREATE, ResourceOps.UPDATE, ResourceOps.SKIP}:
                self._data.resources[resource.local_id] = resource.remote_id

    def _lock(self) -> None:
        """
        Lock state to ensure exclusive write access
        """
        pass

    def _unlock(self) -> None:
        """
        Unlock state after all operations
        """
        pass

    def __enter__(self) -> 'State':
        """
        Do any needed state initialization
        """
        self._lock()
        self._load()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ):
        if self._save_state:
            self._save()
        self._unlock()
