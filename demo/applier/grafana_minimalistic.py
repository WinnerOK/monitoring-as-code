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


def green_fruits_bundle(datasource_uid: str) -> list[GrafanaObject]:
    folder = Folder(title="Fruit bundle")

    data_query = AlertQuery(
        datasourceUid=datasource_uid,
        relativeTimeRange=RelativeTimeRange.last(timedelta(minutes=10)),
        model=PrometheusQuery(
            refId="GreenFruitsCount",
            expr='number_of_fruits{color="green"}',
            interval=Duration("1m"),
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
                        query=data_query.refId,
                        evaluator=GT(param=100),
                    )
                )
            ],
        ),
    )

    alert = Alert(
        folder_title=folder.title,
        evaluation_interval=Duration.from_timedelta(timedelta(seconds=20)),
        for_=Duration.from_timedelta(timedelta(minutes=3)),
        grafana_alert=PostableGrafanaRule(
            condition=expression_query.refId,
            title="GreenFruitLimit",
            data=[data_query, expression_query],
        ),
    )

    return [folder, alert]
