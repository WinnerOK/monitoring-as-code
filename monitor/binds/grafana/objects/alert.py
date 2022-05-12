from binds.grafana.client.refined_models import (
    Duration,
    PostableExtendedRuleNode,
    PostableRuleGroupConfig,
)
from pydantic import Field

from .base import GrafanaObject

__all__ = [
    "Alert",
]


class AlertGroup(PostableRuleGroupConfig):
    def json(
        self,
        *,
        by_alias: bool = True,
        exclude_none: bool = True,
        **kwargs,
    ) -> str:
        return super(AlertGroup, self).json(
            by_alias=by_alias,
            exclude_none=exclude_none,
            **kwargs,
        )


"""
fixme: object attempts to change uid
--- before
+++ after
@@ -65,7 +65,7 @@
     "exec_err_state": "Alerting",
     "no_data_state": "NoData",
     "title": "DemoAlertTitle",
-    "uid": "wkRFEX_nz"
+    "uid": null
   },
"""


class Alert(GrafanaObject, PostableExtendedRuleNode):
    """
    fixme: for a moment I will just generate a single alertGroup per alert
        The reason is that I can't persist in state UIDs of all alerts inside a group
    """

    folder_title: str = Field(...)
    evaluation_interval: Duration = Field(...)

    @classmethod
    def get_remote_identifier(cls, resource_local_id: str) -> str:
        class_name, remote_identifier = resource_local_id.split(".", maxsplit=1)
        if class_name != cls.__name__:
            raise ValueError("Trying to decode invalid id")
        return remote_identifier

    @property
    def local_id(self) -> str:
        return f"{self.folder_title}/{self.grafana_alert.title}"
