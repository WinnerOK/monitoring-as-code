from typing import Iterable, TypeVar

from collections import defaultdict

from controller.exceptions import UnknownResourceHandlerException
from controller.obj import MonitoringObject
from controller.resource import LocalResource, ObsoleteResource, Resource

R = TypeVar("R", bound=Resource)
T = TypeVar("T")


# fixme: подозрительно похожа на _group_resources_by_provider, мб генерализировать
def group_resources(
    resources: Iterable[Resource[MonitoringObject]],
    type_names_to_types: dict[str, type[MonitoringObject]],
) -> dict[type[MonitoringObject], list[Resource[MonitoringObject]]]:
    grouped_resources: dict[
        type[MonitoringObject], list[Resource[MonitoringObject]]
    ] = defaultdict(list)
    unhandled_resources: list[Resource[MonitoringObject]] = []

    for resource in resources:
        match resource:
            case LocalResource(local_object=local_obj):
                obj_type = type(local_obj)
            case ObsoleteResource(local_id=local_id):
                obj_type_name = local_id.split(".", maxsplit=1)[0]
                obj_type = type_names_to_types.get(obj_type_name, None)

        if obj_type:
            grouped_resources[obj_type].append(resource)
        else:
            unhandled_resources.append(resource)

    if unhandled_resources:
        raise UnknownResourceHandlerException(unhandled_resources)

    return grouped_resources
