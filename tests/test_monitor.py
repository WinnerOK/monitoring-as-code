from abc import ABC
from copy import deepcopy

import pytest

from monitor.controller.monitor import Monitor
from monitor.controller.resource import generate_resource_local_id
from monitor.controller.state import RESOURCE_ID_MAPPING
from tests.utils.InmemoryObject import (
    InmemoryObject,
    PrimitiveInmemoryObject,
    NestedPrimitiveInmemoryObject,
    NestedComposeInmemoryObject,
)
from tests.utils.InmemoryProvider import InmemoryProvider
from tests.utils.InmemoryState import InmemoryState


class AbstractTest(ABC):
    @pytest.fixture(
        params=[
            pytest.param(
                PrimitiveInmemoryObject(name="foo", key="primitive"),
                id="Primitive object",
            ),
            pytest.param(
                NestedPrimitiveInmemoryObject(str_list=["foo", "bar"], key="nested"),
                id="Nested object",
            ),
            pytest.param(
                NestedComposeInmemoryObject(
                    key="compose",
                    obj_list=[
                        PrimitiveInmemoryObject(name="foo", key="prim_foo"),
                        PrimitiveInmemoryObject(name="bar", key="prim_bar"),
                    ],
                ),
                id="Compose object",
            ),
        ]
    )
    def obj(self, request) -> InmemoryObject:
        return request.param

    @pytest.fixture()
    def initial_state_objects(self) -> list[InmemoryObject]:
        return []

    @pytest.fixture()
    def initial_remote_objects(self) -> list[InmemoryObject]:
        return []

    @pytest.fixture()
    def initial_state_mapping(self, initial_remote_objects) -> RESOURCE_ID_MAPPING:
        mapping = {}
        for obj in initial_remote_objects:
            local_id = generate_resource_local_id(obj)
            mapping[local_id] = InmemoryProvider.generate_remote_id(local_id)
        return mapping

    @pytest.fixture(name="inmemory_state")
    def inmemory_state_fixture(self, initial_state_mapping):
        return InmemoryState(
            saved_data=initial_state_mapping,
            save_state=True,
            persist_untracked=False,
        )

    @pytest.fixture(name="inmemory_provider")
    def inmemory_provider_fixture(self, initial_remote_objects):
        return InmemoryProvider(remote_objects=initial_remote_objects)

    @pytest.fixture(name="monitor")
    def monitor_fixture(self, inmemory_provider, inmemory_state):
        return Monitor(providers=[inmemory_provider], state=inmemory_state)


class TestCreateNewObject(AbstractTest):
    def test_run(self, obj, monitor, inmemory_provider, inmemory_state):
        monitor.apply_monitoring_state(monitoring_objects=[obj], dry_run=False)

        local_id = generate_resource_local_id(obj)
        expected_remote_id = inmemory_provider.generate_remote_id(local_id)
        assert len(inmemory_state.internal_state.resources) == 1
        assert inmemory_state.internal_state.resources[local_id] == expected_remote_id

        assert len(inmemory_provider.remote_state) == 1
        assert inmemory_provider.remote_state[expected_remote_id] == obj


class TestDeleteObsoleteObject(AbstractTest):
    @pytest.fixture()
    def initial_remote_objects(self, obj) -> list[InmemoryObject]:
        return [obj.copy(deep=True)]

    @pytest.fixture()
    def initial_state_objects(self, obj) -> list[InmemoryObject]:
        return [obj.copy(deep=True)]

    def test_run(self, obj, monitor, inmemory_provider, inmemory_state):
        monitor.apply_monitoring_state(monitoring_objects=[], dry_run=False)

        assert len(inmemory_provider.remote_state) == 0
        assert len(inmemory_state.internal_state.resources) == 0


class TestPersistUnchangedObject(TestDeleteObsoleteObject):
    def test_run(self, obj, monitor, inmemory_provider, inmemory_state):
        initial_state = inmemory_state.internal_state.copy(deep=True)
        initial_remote = deepcopy(inmemory_provider.remote_state)

        monitor.apply_monitoring_state(
            monitoring_objects=[obj.copy(deep=True)],
            dry_run=False,
        )

        assert inmemory_provider.remote_state == initial_remote
        assert inmemory_state.internal_state == initial_state


class TestUpdatePrimitiveObject(AbstractTest):
    @pytest.fixture(
        params=[
            pytest.param(
                (
                    PrimitiveInmemoryObject(name="foo", key="primitive"),
                    PrimitiveInmemoryObject(name="bar", key="primitive"),
                ),
                id="Primitive object",
            ),
            pytest.param(
                (
                    NestedPrimitiveInmemoryObject(
                        str_list=["foo", "bar"], key="nested"
                    ),
                    NestedPrimitiveInmemoryObject(
                        str_list=["foo", "barmen"], key="nested"
                    ),
                ),
                id="Nested object",
            ),
            pytest.param(
                (
                    NestedComposeInmemoryObject(
                        key="compose",
                        obj_list=[
                            PrimitiveInmemoryObject(name="foo", key="prim_foo"),
                            PrimitiveInmemoryObject(name="bar", key="prim_bar"),
                        ],
                    ),
                    NestedComposeInmemoryObject(
                        key="compose",
                        obj_list=[
                            PrimitiveInmemoryObject(name="foo", key="prim_fooler"),
                            PrimitiveInmemoryObject(name="barmen", key="prim_bar"),
                        ],
                    ),
                ),
                id="Compose object",
            ),
        ]
    )
    def change_obj_pair(self, request) -> tuple[InmemoryObject, InmemoryObject]:
        return request.param

    @pytest.fixture()
    def obj(self, request, change_obj_pair) -> InmemoryObject:
        return change_obj_pair[0]

    @pytest.fixture()
    def remote_obj(self, change_obj_pair) -> InmemoryObject:
        return change_obj_pair[1]

    @pytest.fixture()
    def initial_state_objects(self, obj) -> list[InmemoryObject]:
        return [obj.copy(deep=True)]

    @pytest.fixture()
    def initial_remote_objects(self, remote_obj) -> list[InmemoryObject]:
        return [remote_obj.copy(deep=True)]

    def test_run(self, obj, monitor, inmemory_provider, inmemory_state):
        initial_state = inmemory_state.internal_state.copy(deep=True)

        monitor.apply_monitoring_state(
            monitoring_objects=[obj.copy(deep=True)], dry_run=False
        )

        assert inmemory_state.internal_state == initial_state

        remote_id = tuple(initial_state.resources.values())[0]
        assert inmemory_provider.remote_state[remote_id] == obj
