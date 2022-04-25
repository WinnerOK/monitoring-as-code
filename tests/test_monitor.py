import textwrap
from abc import ABC
from copy import deepcopy

import pytest

from monitor.controller.monitor import Monitor
from monitor.controller.resource import generate_resource_local_id
from monitor.controller.state import RESOURCE_ID_MAPPING
from tests.inmemory.InmemoryObject import (
    InmemoryObject,
    NestedComposeInmemoryObject,
    NestedPrimitiveInmemoryObject,
    PrimitiveInmemoryObject,
)
from tests.inmemory.InmemoryProvider import InmemoryProvider
from tests.inmemory.InmemoryState import InmemoryState
from tests.utils import join_param_lists

OBJ_FIXTURE_PARAMS = [
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


class AbstractTest(ABC):
    @pytest.fixture(params=OBJ_FIXTURE_PARAMS)
    def obj(self, request) -> InmemoryObject:
        return request.param

    @pytest.fixture
    def initial_state_objects(self) -> list[InmemoryObject]:
        return []

    @pytest.fixture
    def initial_remote_objects(self) -> list[InmemoryObject]:
        return []

    @pytest.fixture
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
    EXPECTED_DIFF_PARAMS = [
        textwrap.dedent(
            """\
            --- before
            +++ after
            @@ -0,0 +1,4 @@
            +{
            +  "key": "primitive",
            +  "name": "foo"
            +}""",
        ),
        textwrap.dedent(
            """\
            --- before
            +++ after
            @@ -0,0 +1,7 @@
            +{
            +  "key": "nested",
            +  "str_list": [
            +    "foo",
            +    "bar"
            +  ]
            +}""",
        ),
        textwrap.dedent(
            """\
            --- before
            +++ after
            @@ -0,0 +1,13 @@
            +{
            +  "key": "compose",
            +  "obj_list": [
            +    {
            +      "key": "prim_foo",
            +      "name": "foo"
            +    },
            +    {
            +      "key": "prim_bar",
            +      "name": "bar"
            +    }
            +  ]
            +}""",
        ),
    ]

    @pytest.fixture(
        params=join_param_lists(
            OBJ_FIXTURE_PARAMS,
            EXPECTED_DIFF_PARAMS,
            single_value=True,
        )
    )
    def change_obj_data(self, request) -> tuple[InmemoryObject, str]:
        return request.param

    @pytest.fixture
    def obj(self, change_obj_data) -> InmemoryObject:
        return change_obj_data[0]

    @pytest.fixture
    def expected_diff(self, change_obj_data) -> str:
        return change_obj_data[1]

    def test_run(self, obj, monitor, inmemory_provider, inmemory_state):
        monitor.apply_monitoring_state(monitoring_objects=[obj], dry_run=False)

        local_id = generate_resource_local_id(obj)
        expected_remote_id = inmemory_provider.generate_remote_id(local_id)
        assert len(inmemory_state.internal_state.resources) == 1
        assert inmemory_state.internal_state.resources[local_id] == expected_remote_id

        assert len(inmemory_provider.remote_state) == 1
        assert inmemory_provider.remote_state[expected_remote_id] == obj

    def test_diff_shown(self, monitor, obj, expected_diff, caplog):
        monitor.apply_monitoring_state(monitoring_objects=[obj], dry_run=False)

        assert expected_diff in caplog.text


class TestDeleteObsoleteObject(AbstractTest):
    @pytest.fixture
    def initial_remote_objects(self, obj) -> list[InmemoryObject]:
        return [obj.copy(deep=True)]

    @pytest.fixture
    def initial_state_objects(self, obj) -> list[InmemoryObject]:
        return [obj.copy(deep=True)]

    def test_run(self, obj, monitor, inmemory_provider, inmemory_state):
        monitor.apply_monitoring_state(monitoring_objects=[], dry_run=False)

        assert len(inmemory_provider.remote_state) == 0
        assert len(inmemory_state.internal_state.resources) == 0

    def test_diff_shown(self, monitor, obj, caplog):
        monitor.apply_monitoring_state(monitoring_objects=[], dry_run=False)

        expected_diff = f"Diff for {type(obj).__name__}.{obj.key}: deleted"
        assert expected_diff in caplog.text


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
    UPDATED_OBJECTS_PARAMS = [
        PrimitiveInmemoryObject(name="bar", key="primitive"),
        NestedPrimitiveInmemoryObject(str_list=["foo", "barmen"], key="nested"),
        NestedComposeInmemoryObject(
            key="compose",
            obj_list=[
                PrimitiveInmemoryObject(name="foo", key="prim_fooler"),
                PrimitiveInmemoryObject(name="barmen", key="prim_bar"),
            ],
        ),
    ]

    EXPECTED_DIFF_PARAMS = [
        textwrap.dedent(
            """\
            --- before
            +++ after
            @@ -1,4 +1,4 @@
             {
               "key": "primitive",
            -  "name": "bar"
            +  "name": "foo"
             }""",
        ),
        textwrap.dedent(
            """\
            --- before
            +++ after
            @@ -2,6 +2,6 @@
               "key": "nested",
               "str_list": [
                 "foo",
            -    "barmen"
            +    "bar"
               ]
             }""",
        ),
        textwrap.dedent(
            """\
            --- before
            +++ after
            @@ -2,12 +2,12 @@
               "key": "compose",
               "obj_list": [
                 {
            -      "key": "prim_fooler",
            +      "key": "prim_foo",
                   "name": "foo"
                 },
                 {
                   "key": "prim_bar",
            -      "name": "barmen"
            +      "name": "bar"
                 }
               ]
             }""",
        ),
    ]

    @pytest.fixture(
        params=join_param_lists(
            OBJ_FIXTURE_PARAMS,
            UPDATED_OBJECTS_PARAMS,
            EXPECTED_DIFF_PARAMS,
            single_value=True,
        )
    )
    def change_obj_data(self, request) -> tuple[InmemoryObject, InmemoryObject, str]:
        return request.param

    @pytest.fixture
    def obj(self, change_obj_data) -> InmemoryObject:
        return change_obj_data[0]

    @pytest.fixture
    def remote_obj(self, change_obj_data) -> InmemoryObject:
        return change_obj_data[1]

    @pytest.fixture
    def expected_diff(self, change_obj_data) -> str:
        return change_obj_data[2]

    @pytest.fixture
    def initial_state_objects(self, obj) -> list[InmemoryObject]:
        return [obj.copy(deep=True)]

    @pytest.fixture
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

    def test_diff_shown(self, monitor, obj, expected_diff, caplog):
        monitor.apply_monitoring_state(
            monitoring_objects=[obj.copy(deep=True)], dry_run=False
        )

        assert expected_diff in caplog.text
