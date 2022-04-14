from collections import defaultdict
from typing import Dict, Iterable, List, Type, TypeVar

from loguru import logger

from .diff_utils import print_diff
from .exceptions import (
    DuplicatedProviderException,
    UnexpectedResourceStateException,
    UnknownObjectHandlerException,
)
from .obj import MonitoringObject
from .provider import Provider
from .resource import Resource, ResourceAction, ResourceOps
from .state import State

T = TypeVar("T", bound=MonitoringObject)
RESOURCE_ACTION_MAPPING = dict[Resource[T], ResourceOps]


class Monitor:
    def __init__(
        self,
        providers: List[Provider],
        state: State,
    ):
        self._state = state
        self._resource_provider_map: Dict[Type[MonitoringObject], Provider] = {}

        self._register_providers(*providers)

    def _register_providers(self, *providers: Provider):
        # todo: собрать все ошибки и показать их разом
        for provider in providers:
            for operating_object_type in provider.operating_objects:
                if operating_object_type in self._resource_provider_map:
                    raise DuplicatedProviderException()

                self._resource_provider_map[operating_object_type] = provider

    def _group_objects_by_provider(
        self,
        monitoring_objects: Iterable[MonitoringObject],
    ) -> Dict[Provider[T], List[T]]:
        objects_by_provider = defaultdict(list)
        for monitoring_object in monitoring_objects:
            provider = self._resource_provider_map.get(type(monitoring_object), None)
            objects_by_provider[provider].append(monitoring_object)

        if None in objects_by_provider:
            raise UnknownObjectHandlerException(objects_by_provider[None])

        return objects_by_provider

    def apply_monitoring_state(
        self,
        monitoring_objects: Iterable[MonitoringObject],
        dry_run: bool = True,
    ):
        objects_by_provider = self._group_objects_by_provider(monitoring_objects)

        used_providers = objects_by_provider.keys()

        try:
            with self._state as state:
                # todo: Remove once tested
                # resources_by_provider: dict[Provider[T], Iterable[Resource[T]]] = {
                #     provider: [Resource(local_object=obj) for obj in objects]
                #     for provider, objects in objects_by_provider.items()
                # }
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
            # TODO: probably pattern match here
            if resource.remote_object is None and resource.local_object is not None:
                # New resource -> create
                action = ResourceAction(
                    resource=resource,
                    operation=ResourceOps.CREATE,
                )
                print_diff(provider.diff(resource))
            elif resource.remote_object is not None and resource.local_object is None:
                # Obsolete resource -> delete
                action = ResourceAction(
                    resource=resource,
                    operation=ResourceOps.DELETE,
                )
                print_diff(provider.diff(resource))
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
                    print_diff(diff)
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
