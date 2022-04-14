from monitor.binds.grafana.resources import Folder
from monitor.controller.handler import HttpApiResourceHandler


class FolderHandler(HttpApiResourceHandler[Folder]):
    def read(self, resource_id: str) -> Folder:
        response = self.call_api(
            method='GET',
            url=f"/folders/{resource_id}"
        )
        # handle unsuccesfull read
        folder = Folder(**response.json())
        return folder

    def create(self, resource: Folder) -> tuple[Folder, str]:
        response = self.call_api(
            method='POST',
            url='/folders',
            json=resource.dict()
        )
        # todo: parse errors
        return Folder(**response.json()), response.json()['uid']

    def update(self, resource: Folder) -> Folder:
        pass

    def delete(self, resource_id: str) -> None:
        pass
