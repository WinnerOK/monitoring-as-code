from monitor.binds.grafana.client.refined_models import PostableRuleGroupConfig
from controller.api_entity import ApiEntity


class GrafanaAlert(ApiEntity):
    recipient: str = "grafana"

    namespace: str
    alert: PostableRuleGroupConfig

    @property
    def id(self) -> str:
        return self.alert.name
