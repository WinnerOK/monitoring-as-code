from monitor.controller.api_entity import ApiEntity
from monitor.binds.grafana.client.refined_models import PostableRuleGroupConfig


class GrafanaAlert(ApiEntity):
    recipient: str = "grafana"

    namespace: str
    alert: PostableRuleGroupConfig

    @property
    def id(self) -> str:
        return self.alert.name
