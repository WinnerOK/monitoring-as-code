from http import HTTPStatus as status

from binds.grafana.objects.alert import AlertGroup
from controller.handler import HttpApiResourceHandler
from controller.resource import (
    LocalResource,
    MappedResource,
    ObsoleteResource,
    SyncedResource,
)


# fixme: Пока непонятно как делать relation между rulegroup и alert, лучше сделать костыль, который для каждого
#  алерта будет биективно генерить свою собственную группу.
#  Тогда uid будет в rules.[0].grafana_alert.uid
class AlertGroupHandler(HttpApiResourceHandler[AlertGroup]):
    def read(
        self, resource: MappedResource[AlertGroup]
    ) -> SyncedResource[AlertGroup] | ObsoleteResource[AlertGroup]:
        response = self.client.get(f"ruler/grafana/api/v1/rules/{resource.remote_id}")

        if response.status_code == status.NOT_FOUND:
            return ObsoleteResource(
                local_id=resource.local_id,
                remote_id=resource.remote_id,
            )
        elif response.status_code == status.ACCEPTED:
            json = response.json()
            alert_group = AlertGroup(
                folder_title=resource.local_object.folder_name,
                **json,
            )
            return SyncedResource(
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
        alert_group = AlertGroup(
            folder_title=resource.local_object.folder_name,
            **json,
        )

        return SyncedResource(
            local_object=resource.local_object,
            remote_id=resource.local_id,
            remote_object=alert_group,
        )

    def update(
        self, resource: SyncedResource[AlertGroup]
    ) -> SyncedResource[AlertGroup]:
        pass

    def delete(self, resource: ObsoleteResource[AlertGroup]) -> None:
        pass
