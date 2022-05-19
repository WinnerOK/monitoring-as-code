from http import HTTPStatus as Status

from binds.grafana.objects import Folder
from controller.handler import HttpApiResourceHandler
from controller.resource import (
    LocalResource,
    MappedResource,
    ObsoleteResource,
    SyncedResource,
)


class FolderHandler(HttpApiResourceHandler[Folder]):
    def read(
        self,
        resource: MappedResource[Folder],
    ) -> SyncedResource[Folder] | ObsoleteResource[Folder]:
        # Get folder by uid
        response = self.client.get(f"folders/{resource.remote_id}")

        if response.status_code == Status.NOT_FOUND:
            return ObsoleteResource(
                local_id=resource.local_id,
                remote_id=resource.remote_id,
            )
        elif response.status_code == Status.OK:
            json = response.json()
            folder = Folder(**json)
            return SyncedResource(
                local_object=resource.local_object,
                remote_id=resource.remote_id,
                remote_object=folder,
            )
        else:
            raise RuntimeError(f"Unexpected status: {response.status_code}")

    def create(
        self,
        resource: LocalResource[Folder],
    ) -> SyncedResource[Folder]:
        response = self.client.post("folders", json=resource.local_object.dict())
        response.raise_for_status()

        json = response.json()
        remote_folder = Folder(**json)
        remote_id = json["uid"]

        return SyncedResource(
            local_object=resource.local_object,
            remote_object=remote_folder,
            remote_id=remote_id,
        )

    def update(
        self,
        resource: SyncedResource[Folder],
    ) -> SyncedResource[Folder]:
        response = self.client.put(
            f"folders/{resource.remote_id}",
            json={
                "overwrite": True,
                **resource.local_object.dict(),
            },
        )

        response.raise_for_status()

        json = response.json()
        remote_folder = Folder(**json)

        updated_resource = resource.copy(deep=True)
        updated_resource.remote_object = remote_folder

        return updated_resource

    def delete(
        self,
        resource: ObsoleteResource[Folder],
    ) -> None:
        response = self.client.delete(
            f"folders/{resource.remote_id}",
            data={
                # fail deletion if folder contains Grafana 8 alerts
                "forceDeleteRules": False,
            },
        )

        if response.status_code == Status.NOT_FOUND:
            return

        response.raise_for_status()
