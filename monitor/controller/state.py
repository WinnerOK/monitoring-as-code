from abc import ABC, abstractmethod
from types import TracebackType
from typing import Iterable, Optional, Type

from pydantic import BaseModel

from .obj import MonitoringObject
from .resource import (
    IdType,
    LocalResource,
    MappedResource,
    ObsoleteResource,
    SyncedResource,
)

RESOURCE_ID_MAPPING = dict[IdType, IdType]  # local_id: remote_id


class StateData(BaseModel):
    resources: RESOURCE_ID_MAPPING = {}


class State(ABC):
    def __init__(
        self,
        *,
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

    @abstractmethod
    def _save(self) -> None:
        """
        Persist self._data
        Do not consider self._save_stave; It is already handled in self.__exit__
        """

    def fill_provider_id(
        self,
        local_resources: Iterable[LocalResource[MonitoringObject]],
    ) -> list[LocalResource[MonitoringObject] | MappedResource[MonitoringObject]]:
        rv = []
        for local_resource in local_resources:
            if (local_id := local_resource.local_id) in self._data.resources:
                rv.append(
                    MappedResource.from_local(
                        local_resource,
                        self._data.resources[local_id],
                    )
                )
            else:
                rv.append(local_resource)
        return rv

    def get_untracked_resources(
        self, resources: Iterable[LocalResource[MonitoringObject]]
    ) -> list[ObsoleteResource[MonitoringObject]]:
        """
        Return list of resources that are in state, but were not passed as parameters
        """
        if self._persist_untracked:
            return []

        tracked_resource_local_ids = {
            tracked_resource.local_id for tracked_resource in resources
        }
        untracked_resources = [
            ObsoleteResource(
                local_id=local_id,
                remote_id=remote_id,
            )
            for local_id, remote_id in self._data.resources.items()
            if local_id not in tracked_resource_local_ids
        ]
        return untracked_resources

    def update_state(
        self,
        resources: Iterable[
            SyncedResource[MonitoringObject] | ObsoleteResource[MonitoringObject]
        ],
    ) -> None:
        for resource in resources:
            match resource:
                case ObsoleteResource(local_id=local_id):
                    self._data.resources.pop(local_id, None)
                case SyncedResource(local_id=local_id, remote_id=remote_id):
                    self._data.resources[local_id] = remote_id

    def _lock(self) -> None:
        """
        Lock state to ensure exclusive write access
        """

    def _unlock(self) -> None:
        """
        Unlock state after all operations
        """

    def __enter__(self) -> "State":
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
    ) -> None:
        if self._save_state:
            self._save()
        self._unlock()
