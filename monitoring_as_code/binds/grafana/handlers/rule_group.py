from http import HTTPStatus as Status

from binds.grafana.objects.alert import AlertGroup
from controller.handler import HttpApiResourceHandler
from controller.resource import (
    LocalResource,
    MappedResource,
    ObsoleteResource,
    SyncedResource,
)


class AlertGroupHandler(HttpApiResourceHandler[AlertGroup]):
    def read(
        self, resource: MappedResource[AlertGroup]
    ) -> SyncedResource[AlertGroup] | ObsoleteResource[AlertGroup]:
        response = self.client.get(f"ruler/grafana/api/v1/rules/{resource.remote_id}")

        if response.status_code == Status.NOT_FOUND:
            return ObsoleteResource(
                local_id=resource.local_id,
                remote_id=resource.remote_id,
            )
        elif response.status_code == Status.ACCEPTED:
            json = response.json()
            alert_group = AlertGroup(**json)
            return SyncedResource[AlertGroup](
                local_object=resource.local_object,
                remote_id=resource.remote_id,
                remote_object=alert_group,
            )
        else:
            raise RuntimeError(f"Unexpected status: {response.status_code}")

    def create(self, resource: LocalResource[AlertGroup]) -> SyncedResource[AlertGroup]:
        response = self.client.post(
            f"ruler/grafana/api/v1/rules/{resource.local_object.folder_name}",
            json=resource.local_object.dict(),
        )
        response.raise_for_status()

        json = response.json()
        alert_group = AlertGroup(**json)

        return SyncedResource[AlertGroup](
            local_object=resource.local_object,
            remote_id=resource.local_id,
            remote_object=alert_group,
        )

    def update(
        self, resource: SyncedResource[AlertGroup]
    ) -> SyncedResource[AlertGroup]:
        raise NotImplementedError()

    def delete(self, resource: ObsoleteResource[AlertGroup]) -> None:
        raise NotImplementedError()
