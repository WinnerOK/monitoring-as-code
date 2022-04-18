from collections import defaultdict
from typing import Dict, Iterable, Type, TypeVar, cast

from loguru import logger

from monitor.controller.diff_utils import print_diff, calculate_diff
from monitor.controller.exceptions import (
    DuplicatedProviderException,
    UnknownResourceHandlerException,
)
from monitor.controller.obj import MonitoringObject
from monitor.controller.provider import Provider
from monitor.controller.resource import (
    Resource,
    ResourceOps,
    LocalResource,
    ObsoleteResource,
    MappedResource,
    SyncedResource,
)
from monitor.controller.state import State

T = TypeVar("T", bound=MonitoringObject)
RESOURCE_ACTION_MAPPING = dict[Resource[T], ResourceOps]


class Monitor:
    def __init__(
        self,
        providers: list[Provider[T]],
        state: State,
    ):
        self._state = state
        self._resource_provider_map: Dict[Type[T], Provider[T]] = {}
        self._resource_name_provider_map: Dict[str, Provider[T]] = {}
        self._providers: list[Provider[T]] = []

        self._register_providers(*providers)

    def _register_providers(self, *providers: Provider[T]) -> None:
        # todo: собрать все ошибки и показать их разом
        for provider in providers:
            for operating_object_type in provider.operating_objects:
                if operating_object_type in self._resource_provider_map:
                    raise DuplicatedProviderException()

                self._resource_provider_map[operating_object_type] = provider
                self._resource_name_provider_map[
                    operating_object_type.__name__
                ] = provider
                self._providers.append(provider)

    def _group_resources_by_provider(
        self,
        resources: Iterable[Resource[MonitoringObject]],
    ) -> dict[Provider[MonitoringObject], list[Resource[MonitoringObject]]]:
        resources_by_provider: dict[
            Provider[MonitoringObject], list[Resource[MonitoringObject]]
        ] = defaultdict(list)
        unhandled_resources: list[Resource[MonitoringObject]] = []

        for resource in resources:
            # todo: check if mypy finds pattern matching exhaustive
            # Since Resource class is ABC, this two cases cover everythinb
            match resource:
                case LocalResource(local_object=local_obj):
                    provider = self._resource_provider_map.get(type(local_obj), None)
                case ObsoleteResource(local_id=local_id):
                    class_name = local_id.split(".", maxsplit=1)[0]
                    provider = self._resource_name_provider_map.get(class_name, None)

            if provider:
                resources_by_provider[provider].append(resource)
            else:
                unhandled_resources.append(resource)

        if unhandled_resources:
            raise UnknownResourceHandlerException(unhandled_resources)

        return resources_by_provider

    def apply_monitoring_state(
        self,
        monitoring_objects: list[MonitoringObject],
        dry_run: bool = True,
    ) -> None:

        local_resources: list[LocalResource[MonitoringObject]] = [
            LocalResource(local_object=local_obj) for local_obj in monitoring_objects
        ]

        try:
            with self._state as state:
                operating_resources: list[
                    Resource[MonitoringObject]
                ] = state.fill_provider_id(local_resources)

                operating_resources.extend(
                    state.get_untracked_resources(local_resources)
                )

                grouped_resources = self._group_resources_by_provider(
                    operating_resources
                )

                provider: Provider[T]
                resources: list[Resource[T]]
                for provider, resources in grouped_resources.items():
                    mapped_resources: list[MappedResource[T]] = []
                    processed_resources: list[
                        ObsoleteResource[T] | SyncedResource[T] | LocalResource[T]
                    ] = []

                    for r in resources:
                        if isinstance(r, MappedResource):
                            mapped_resources.append(r)
                        else:
                            processed_resources.append(r)

                    processed_resources.extend(
                        provider.sync_resources(mapped_resources)
                    )

                    (
                        need_removal,
                        need_update,
                        skip_update,
                    ) = self._print_diff_split_resources(provider, processed_resources)
                    if not dry_run:
                        updated_resources = provider.apply_actions(
                            need_update + need_removal
                        )
                        state.update_state(
                            updated_resources + skip_update + need_removal
                        )

        finally:
            for provider in self._providers:
                provider.dispose()

    def _print_diff_split_resources(
        self,
        provider: Provider[T],
        provider_resources: Iterable[Resource[T]],
    ):
        need_removal: list[ObsoleteResource[T]] = []
        need_update: list[SyncedResource[T] | LocalResource[T]] = []
        skip_update: list[SyncedResource[T]] = []

        for resource in provider_resources:
            diff_header = f"Diff for {resource.local_id}"  # type: ignore  # weird pydantic issue, that property does
            # not override field class

            match resource:
                case ObsoleteResource():
                    logger.info(diff_header + ": deleted")
                    need_removal.append(cast(ObsoleteResource[T], resource))
                case SyncedResource():
                    synced_res = cast(SyncedResource[T], resource)
                    diff = provider.diff(synced_res)
                    if diff:
                        print_diff(diff_header, diff)
                        need_update.append(synced_res)
                    else:
                        skip_update.append(synced_res)
                case LocalResource(local_object=obj):
                    print_diff(diff_header, calculate_diff(None, obj))
                    need_update.append(cast(LocalResource[T], resource))

        return need_removal, need_update, skip_update
