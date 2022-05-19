from http import HTTPStatus as Status

from binds.grafana.objects.alert import Alert, AlertGroup
from controller.handler import HttpApiResourceHandler
from controller.resource import (
    LocalResource,
    MappedResource,
    ObsoleteResource,
    SyncedResource,
)


def alert_to_singleton_group(alert: Alert) -> AlertGroup:
    return AlertGroup(
        # folder_title=alert.local_id,
        interval=alert.evaluation_interval,
        name=alert.grafana_alert.title,
        rules=[alert],
    )


def parse_singleton_group(group: AlertGroup, folder_title: str) -> Alert:
    if (rules_length := len(group.rules)) != 1:
        raise ValueError(
            "AlertGroup %s has %d alerts, but expected to be a singleton"
            % (group.name, rules_length)
        )

    return Alert(
        evaluation_interval=group.interval,
        folder_title=folder_title,
        **group.rules[0].dict(),
    )


class AlertHandler(HttpApiResourceHandler[Alert]):
    def read(
        self, resource: MappedResource[Alert]
    ) -> SyncedResource[Alert] | ObsoleteResource[Alert]:
        remote_identifier = Alert.get_remote_identifier(resource.local_id)
        response = self.client.get(f"ruler/grafana/api/v1/rules/{remote_identifier}")
        if response.status_code == Status.NOT_FOUND:
            return ObsoleteResource(
                local_id=resource.local_id,
                remote_id=resource.remote_id,
            )
        elif response.status_code == Status.ACCEPTED:
            json = response.json()
            alert_group = AlertGroup(**json)
            alert_id = alert_group.rules[0].grafana_alert.uid
            return SyncedResource(
                local_object=resource.local_object,
                remote_id=alert_id,
                remote_object=parse_singleton_group(
                    alert_group, resource.local_object.folder_title
                ),
            )
        else:
            raise RuntimeError(f"Unexpected status: {response.status_code}")

    def create(self, resource: LocalResource[Alert]) -> SyncedResource[Alert]:
        folder_name = resource.local_object.folder_title
        alert_group = alert_to_singleton_group(resource.local_object)

        response = self.client.post(
            f"ruler/grafana/api/v1/rules/{folder_name}",
            data=alert_group.json(),
        )
        response.raise_for_status()

        created_resource = self.read(
            MappedResource(local_object=resource.local_object, remote_id="unknown")
        )

        if isinstance(created_resource, ObsoleteResource):
            raise RuntimeError("After creation, read must return Synced resource")

        return created_resource

    def update(self, resource: SyncedResource[Alert]) -> SyncedResource[Alert]:
        group = alert_to_singleton_group(resource.local_object)
        group.rules[0].grafana_alert.uid = resource.remote_id

        folder_title = resource.local_object.folder_title

        response = self.client.post(
            f"ruler/grafana/api/v1/rules/{folder_title}",
            data=group.json(),
        )
        response.raise_for_status()

        updated_resource = self.read(
            MappedResource(
                local_object=resource.local_object, remote_id=resource.remote_id
            )
        )

        if isinstance(updated_resource, ObsoleteResource):
            raise RuntimeError("After creation, read must return Synced resource")

        return updated_resource

    def delete(self, resource: ObsoleteResource[Alert]) -> None:
        remote_identifier = Alert.get_remote_identifier(resource.local_id)

        response = self.client.delete(
            f"ruler/grafana/api/v1/rules/{remote_identifier}",
        )
        if response.status_code == Status.NOT_FOUND:
            return

        response.raise_for_status()
