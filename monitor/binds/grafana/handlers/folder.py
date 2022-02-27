from monitor.binds.grafana.resources import Folder
from monitor.controller.handler import HttpApiResourceHandler


class FolderHandler(HttpApiResourceHandler[Folder]):
    def read(self, resource_id: str) -> Folder:
        response = self.call_api(
            method='GET',
            url=f"/folders/{resource_id}"
        )
        folder = Folder(**response.json())
        return folder

    def create(self, resource: Folder) -> Folder:
        pass

    def update(self, resource: Folder) -> Folder:
        pass

    def delete(self, resource_id: str) -> None:
        pass
