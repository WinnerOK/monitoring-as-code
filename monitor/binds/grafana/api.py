from binds.grafana.alert import GrafanaAlert
from controller.api_entity import ID_TYPE
from controller.api import API


class GrafanaAPI(API[GrafanaAlert]):
    def read(self, object_id: ID_TYPE) -> GrafanaAlert:
        return GrafanaAlert(id=1)

    def update(self, entity: GrafanaAlert) -> GrafanaAlert:
        return GrafanaAlert(id=1)

    def delete(self, object_id: ID_TYPE) -> None:
        pass

    def create(self, entity: GrafanaAlert) -> GrafanaAlert:
        return GrafanaAlert(id=1)
