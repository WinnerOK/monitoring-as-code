from datetime import timedelta

from binds.grafana.client.alert_queries import ClassicExpression, PrometheusQuery
from binds.grafana.client.alert_queries.classic_conditions import (
    GT,
    ClassicCondition,
    Reducers,
)
from binds.grafana.client.alert_queries.classic_conditions import dictify_condition as d
from binds.grafana.client.alerting import AlertQuery, PostableGrafanaRule
from binds.grafana.client.types import Duration, RelativeTimeRange
from binds.grafana.objects import Alert, Folder, GrafanaObject


def get_checks(datasource_uid: str) -> list[GrafanaObject]:

    demo_folder = Folder(title="sandbox_folder")

    prometheus_query = AlertQuery(
        datasourceUid=datasource_uid,
        relativeTimeRange=RelativeTimeRange.last(timedelta(minutes=10)),
        model=PrometheusQuery(
            refId="DataQuery",
            expr='100 * scrape_duration_seconds{instance="prometheus-data-generator:9000"}',
            maxDataPoints=43200,
            interval=Duration("10s"),
        ),
    )

    expression_query = AlertQuery(
        relativeTimeRange=RelativeTimeRange.instant(),
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

    return [
        demo_folder,
        demo_alert,
        another_demo_alert,
    ]
