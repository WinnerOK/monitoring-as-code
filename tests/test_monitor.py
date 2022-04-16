from abc import ABC

import pytest

from monitor.controller.monitor import Monitor
from monitor.controller.state import RESOURCE_ID_MAPPING
from tests.utils.InmemoryObject import InmemoryObject, PrimitiveInmemoryObject
from tests.utils.InmemoryProvider import InmemoryProvider
from tests.utils.InmemoryState import InmemoryState


class AbstractTest(ABC):
    def initial_state_mapping(self) -> RESOURCE_ID_MAPPING:
        return {}

    def initial_remote_objects(self) -> list[InmemoryObject]:
        return []

    @pytest.fixture(name="inmemory_state")
    def inmemory_state_fixture(self):
        return InmemoryState(
            saved_data=self.initial_state_mapping(),
            save_state=True,
            persist_untracked=True,
        )

    @pytest.fixture(name="inmemory_provider")
    def inmemory_provider_fixture(self):
        return InmemoryProvider(remote_objects=self.initial_remote_objects())

    @pytest.fixture(name="monitor")
    def monitor_fixture(self, inmemory_provider, inmemory_state):
        return Monitor(providers=[inmemory_provider], state=inmemory_state)


class TestCreateNewObject(AbstractTest):
    def test_create(self, monitor, inmemory_provider, inmemory_state):
        obj = PrimitiveInmemoryObject(name="foo")

        monitor.apply_monitoring_state(monitoring_objects=[obj], dry_run=False)

        expected_remote_id = inmemory_provider.generate_remote_id(obj.local_id)
        assert len(inmemory_state.internal_state.resources) == 1
        assert (
            inmemory_state.internal_state.resources[obj.local_id] == expected_remote_id
        )

        assert len(inmemory_provider.remote_state) == 1
        assert inmemory_provider.remote_state[expected_remote_id] == obj


class TestDeleteObsoleteObject(AbstractTest):

    old_obj = PrimitiveInmemoryObject(name="foo")

    def initial_remote_objects(self) -> list[InmemoryObject]:
        return [self.old_obj]

    def initial_state_mapping(self) -> RESOURCE_ID_MAPPING:
        return {
            self.old_obj.local_id: InmemoryProvider.generate_remote_id(
                self.old_obj.local_id
            )
        }

    def test_delete(self, monitor, inmemory_provider, inmemory_state):
        monitor.apply_monitoring_state(monitoring_objects=[], dry_run=False)

        assert len(inmemory_provider.remote_state) == 0
        assert len(inmemory_state.internal_state.resources) == 0
