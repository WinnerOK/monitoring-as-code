from datetime import timedelta

import requests

from monitor.binds.grafana.alert import GrafanaAlert
from monitor.binds.grafana.client.refined_models import (
    Duration,
    PostableRuleGroupConfig,
    PostableExtendedRuleNode,
    PostableGrafanaRule,
    ExecErrState,
    NoDataState,
    AlertQuery,
    RelativeTimeRange,
)

username = "admin"
password = "admin"
namespace = "MAAC demo"
PROMETHEUS_UID = "UyZh4UK7z"

query1 = AlertQuery(
    refId="A",
    datasourceUid=PROMETHEUS_UID,
    relativeTimeRange=RelativeTimeRange(
        from_=Duration.parse_obj(timedelta(minutes=5)),
        to=Duration.parse_obj(timedelta(seconds=0)),
    ),
    model={
        "refId": "A",
        "expr": 'scrape_duration_seconds{instance="prometheus-data-generator:9000"}',
        "interval": "",
        "intervalMs": 1000,
        "legendFormat": "",
        "maxDataPoints": 43200,
    },
)
query2 = AlertQuery(
    refId="B",
    relativeTimeRange=RelativeTimeRange(
        from_=Duration.parse_obj(timedelta(seconds=0)),
        to=Duration.parse_obj(timedelta(seconds=0)),
    ),
    datasourceUid="-100",
    model={
        "intervalMs": 1000,
        "maxDataPoints": 43200,
        "type": "classic_conditions",
        "datasource": "__expr__",
        "conditions": [
            {
                "evaluator": {"params": [0.01], "type": "gt"},
                "operator": {"type": "and"},
                "query": {"params": ["A"]},
                "reducer": {"params": [], "type": "last"},
                "type": "query",
            }
        ],
    },
)
grafana_alert = PostableGrafanaRule(
    condition=query2.refId,
    # Actually displayed alert name
    title="WE_GrafanaAlertTitle",
    exec_err_state=ExecErrState.Alerting,
    no_data_state=NoDataState.Alerting,
    data=[
        query1,
        query2,
    ],
)

# Rule aka Annotated Alert
postable_extended_rule_node = PostableExtendedRuleNode(
    # This name is not displayed anywhere, use grafana_alert.title
    alert="WatchEye alert",
    annotations={
        "WE_ann": "lol",
    },
    for_=Duration.parse_obj(timedelta(minutes=5)),
    labels={"lb1": "val"},
    grafana_alert=grafana_alert,
)

# Actually a RoleGroup; Each rule -- an alert
alert = PostableRuleGroupConfig(
    # RoleGroup name
    name="WatchEye Alert",
    interval=Duration.parse_obj(timedelta(seconds=35)),
    rules=[postable_extended_rule_node],
)


alert_wrapper = GrafanaAlert(
    namespace=namespace,
    recipient="grafana",
    alert=alert,
)

rv = requests.post(
    url=f"http://localhost:3000/api/ruler/grafana/api/v1/rules/{namespace}/",
    auth=(username, password),
    headers={
        'Content-type': 'application/json',
    },
    json=alert_wrapper.alert.json(by_alias=True),
)

print(rv.json())
rv.raise_for_status()
