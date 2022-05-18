from datetime import timedelta
from pathlib import Path
from urllib.parse import urljoin

from binds.grafana.client.alert_queries import ClassicExpression, PrometheusQuery
from binds.grafana.client.alert_queries.classic_conditions import (
    GT,
    ClassicCondition,
    Reducers,
)
from binds.grafana.client.alert_queries.classic_conditions import dictify_condition as d
from binds.grafana.client.alerting import AlertQuery, PostableGrafanaRule
from binds.grafana.client.types import Duration, RelativeTimeRange
from binds.grafana.grafana_provider import GrafanaProvider
from binds.grafana.objects import Folder, Alert
from controller.monitor import Monitor
from controller.states import FileState
from loguru import logger
from requests import HTTPError, Response, Session

USERNAME = "admin"
PASSWORD = "admin"
DATASOURCE_UID = "UyZh4UK7z"


class BaseUrlSession(Session):
    def __init__(self, prefix_url=None):
        super().__init__()
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs) -> Response:
        url = urljoin(self.prefix_url, url)
        return super().request(method, url, *args, **kwargs)


grafana_session = BaseUrlSession(prefix_url="http://localhost:10050/api/")
grafana_session.auth = (USERNAME, PASSWORD)

grafana_provider = GrafanaProvider(grafana_session)

state = FileState(
    Path("./state.json"),
    save_state=True,
    persist_untracked=False,
)

monitor = Monitor(
    providers=[grafana_provider],
    state=state,
)

demo_folder = Folder(title="sandbox_folder")

prometheus_query = AlertQuery(
    datasourceUid=DATASOURCE_UID,
    relativeTimeRange=RelativeTimeRange(
        from_=10 * 60,
    ),
    model=PrometheusQuery(
        refId="DataQuery",
        expr='100 * scrape_duration_seconds{instance="prometheus-data-generator:9000"}',
        maxDataPoints=43200,
        interval=Duration("10s"),
    ),
)
expression_query = AlertQuery(
    relativeTimeRange=RelativeTimeRange(
        from_=0,
    ),
    datasourceUid="-100",
    model=ClassicExpression(
        refId="AlertCond",
        conditions=[
            d(
                ClassicCondition(
                    reducer=Reducers.LAST,
                    query=prometheus_query.refId,
                    evaluator=GT(param=0.2),
                )
            )
        ],
    ),
)

demo_alert = Alert(
    folder_title=demo_folder.title,
    evaluation_interval=Duration.from_timedelta(timedelta(seconds=10)),
    annotations={
        "ann1": "ann11Value",
    },
    labels={
        "label1": "label1Value",
    },
    for_=Duration.from_timedelta(timedelta(seconds=30)),
    grafana_alert=PostableGrafanaRule(
        condition=expression_query.refId,
        title="DemoAlertTitle",
        data=[
            prometheus_query,
            expression_query,
        ],
    ),
)

another_demo_alert = demo_alert.copy(deep=True)
another_demo_alert.grafana_alert.title = "Different_alert"

try:
    monitor.apply_monitoring_state(
        monitoring_objects=[
            demo_folder,
            demo_alert,
            another_demo_alert,
        ],
        dry_run=True,
        # dry_run=False,
    )
except HTTPError as e:
    logger.debug(e.response.json())
    raise e
