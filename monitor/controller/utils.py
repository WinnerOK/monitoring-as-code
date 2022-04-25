from .obj import MonitoringObject
from .resource import LocalResource, ObsoleteResource


def get_resource_object_type_name(
    r: LocalResource[MonitoringObject] | ObsoleteResource[MonitoringObject],
) -> str:
    match r:
        case LocalResource(local_object=obj):
            return type(obj).__name__
        case ObsoleteResource(local_id=local_id):
            return local_id.split(".", maxsplit=1)[0]
