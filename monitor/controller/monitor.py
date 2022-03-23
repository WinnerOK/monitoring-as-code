from collections import defaultdict
from typing import List, Dict, Type, Iterable

from .provider import Provider
from .resource import Resource
from .exceptions import UnknownResourceHandler


class Monitor:
    def __init__(self, providers: List[Provider]):
        self.resource_provider_map: Dict[Type[Resource], Provider] = {}
        self.register_providers(*providers)

    def register_providers(self, *providers: Provider):
        self.resource_provider_map.update(
            {
                operating_resource_type: provider
                for provider in providers
                for operating_resource_type in provider.operating_resources
            }
        )

    def _group_resources_by_provider(self, resources: Iterable[Resource]) -> Dict[Provider, List[Resource]]:
        resources_by_provider = defaultdict(list)
        for resource in resources:
            provider = self.resource_provider_map.get(type(resource), None)
            resources_by_provider[provider].append(resource)

        if None in resources_by_provider:
            raise UnknownResourceHandler(resources_by_provider[None])

        return resources_by_provider

    def apply_state(self, *resources: Resource, dry_run_only: bool = True):
        resources_by_provider = self._group_resources_by_provider(resources)

        for provider, resources in resources_by_provider.items():
            # todo probably somehow return diff and render here; otherwise render in provider
            provider.process_resources(resources, dry_run=True)

        if dry_run_only:
            return


