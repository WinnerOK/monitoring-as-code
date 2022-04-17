from typing import Dict, Iterable, Type, TypeVar, Optional, cast

from collections import defaultdict

from loguru import logger

from monitor.controller.diff_utils import print_diff
from monitor.controller.exceptions import (
    DuplicatedProviderException,
    UnexpectedResourceStateException,
    UnknownObjectHandlerException,
)
from monitor.controller.obj import MonitoringObject
from monitor.controller.provider import Provider
from monitor.controller.resource import Resource, ResourceAction, ResourceOps
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

        self._register_providers(*providers)

    def _register_providers(self, *providers: Provider[T]) -> None:
        # todo: собрать все ошибки и показать их разом
        for provider in providers:
            for operating_object_type in provider.operating_objects:
                if operating_object_type in self._resource_provider_map:
                    raise DuplicatedProviderException()

                self._resource_provider_map[operating_object_type] = provider

    def _group_objects_by_provider(
        self,
        monitoring_objects: Iterable[MonitoringObject],
    ) -> dict[Provider[T], list[T]]:
        # fixme: return type annotation says about specific type T
        # instead of some type T; In mypy it is impossible to annotate "some T"
        # so rework main workflow to get rid of such annotation
        objects_by_provider: dict[Provider[T], list[T]] = defaultdict(list)
        unhandled_objects: list[MonitoringObject] = []
        for monitoring_object in monitoring_objects:
            provider = self._resource_provider_map.get(type(monitoring_object), None)
            if provider is None:
                unhandled_objects.append(monitoring_object)
            else:
                objects_by_provider[provider].append(monitoring_object)

        if unhandled_objects:
            raise UnknownObjectHandlerException(unhandled_objects)

        return objects_by_provider

    def apply_monitoring_state(
        self,
        monitoring_objects: list[MonitoringObject],
        dry_run: bool = True,
    ) -> None:
        objects_by_provider = self._group_objects_by_provider(monitoring_objects)

        used_providers = objects_by_provider.keys()

        try:
            with self._state as state:
                # fixme: из стейта нужно подгружать untracked ресурсы, иначе они теряются
                # Тк из стейта подгружаются только айдишники, надо уметь разделять ресурсы не только по типу объекта,
                # но и по айдишнику. Для этого в id всегда должна быть зашита информация о типе ресурса

                resources_by_provider: dict[Provider[T], Iterable[Resource[T]]] = {}
                for provider, local_objects in objects_by_provider.items():
                    local_resources = [
                        Resource(local_object=obj) for obj in local_objects
                    ]
                    state.fill_provider_id(local_resources)
                    resources_by_provider[provider] = local_resources

                # can be async
                for provider, resources in resources_by_provider.items():
                    synced_resources = provider.sync_resources(resources)
                    resources_by_provider[provider] = synced_resources

                resource_actions_by_provider: dict[
                    Provider[T], list[ResourceAction[T]]
                ] = {
                    provider: self._calculate_actions(provider, synced_resources)
                    for provider, synced_resources in resources_by_provider.items()
                }

                if not dry_run:
                    for (
                        provider,
                        resource_actions,
                    ) in resource_actions_by_provider.items():
                        provider.apply_actions(resource_actions)
                        state.update_state(resource_actions)

        finally:
            for provider in used_providers:
                provider.dispose()

    def _calculate_actions(
        self,
        provider: Provider[T],
        provider_resources: Iterable[Resource[T]],
    ) -> list[ResourceAction[T]]:
        logger.info("Calculating actions on resources")
        resource_actions = []

        unexpected_state_resources = []
        for resource in provider_resources:
            diff_header = f"Diff for {resource.local_id}"
            # TODO: probably pattern match here
            if resource.remote_object is None and resource.local_object is not None:
                # New resource -> create
                action = ResourceAction(
                    resource=resource,
                    operation=ResourceOps.CREATE,
                )
                print_diff(diff_header, provider.diff(resource))
            elif resource.remote_object is not None and resource.local_object is None:
                # Obsolete resource -> delete
                action = ResourceAction(
                    resource=resource,
                    operation=ResourceOps.DELETE,
                )
                print_diff(diff_header, provider.diff(resource))
            elif (
                resource.remote_object is not None and resource.local_object is not None
            ):
                # Either SKIP if same, or UPDATE
                diff = provider.diff(resource)
                if diff:
                    action = ResourceAction(
                        resource=resource,
                        operation=ResourceOps.UPDATE,
                    )
                    print_diff(diff_header, diff)
                else:
                    action = ResourceAction(
                        resource=resource,
                        operation=ResourceOps.SKIP,
                    )
            else:
                # resource.remote_object is None and resource.local_object is None:
                # Strange object: how it even get to such state?
                # Just ignore it
                unexpected_state_resources.append(resource)
                action = ResourceAction(
                    resource=resource,
                    operation=ResourceOps.IGNORE,
                )

            resource_actions.append(action)

        if unexpected_state_resources:
            raise UnexpectedResourceStateException(unexpected_state_resources)

        return resource_actions
