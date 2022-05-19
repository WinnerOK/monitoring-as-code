from typing import ContextManager

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from time import perf_counter, process_time
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
from binds.grafana.objects import Alert, Folder
from controller.monitor import Monitor
from controller.states import FileState
from loguru import logger
from requests import Response, Session

USERNAME = "admin"
PASSWORD = "admin"
DATASOURCE_UID = "PrometheusUID"


class Timer(ContextManager):
    def __init__(self):
        self._start_clock: float | None = None
        self._start_processor: float | None = None

        self.clock_time: float | None = None
        self.processor_time: float | None = None

    def __enter__(self):
        self._start_clock = perf_counter()
        self._start_processor = process_time()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clock_time = perf_counter() - self._start_clock
        self.processor_time = process_time() - self._start_processor


class BaseUrlSession(Session):
    def __init__(self, prefix_url=None):
        super().__init__()
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs) -> Response:
        url = urljoin(self.prefix_url, url)
        return super().request(method, url, *args, **kwargs)


def run(
    monitor: Monitor,
    alert_count: int,
    dry_run: bool,
    custom_label="Some Initial Value",
) -> tuple[float, float]:

    folder = Folder(title="Performance folder")

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

    reference_alert = Alert(
        folder_title=folder.title,
        evaluation_interval=Duration.from_timedelta(timedelta(seconds=10)),
        annotations={
            "ann1": "ann11Value",
        },
        labels={
            "label1": "label1Value",
            "custom_label": custom_label,
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

    monitored_objects = [folder, reference_alert]
    for idx in range(alert_count - 1):
        copied_alert = reference_alert.copy(deep=True)
        copied_alert.grafana_alert.title = f"copy{idx}"

        monitored_objects.append(copied_alert)

    with Timer() as t:
        monitor.apply_monitoring_state(
            monitored_objects,
            dry_run=dry_run,
        )

    return t.clock_time, t.processor_time


def cleanup(monitor: Monitor):
    with Timer() as t:
        monitor.apply_monitoring_state(monitoring_objects=[], dry_run=False)
    return t.clock_time, t.processor_time


@dataclass
class Measurement:
    cleanup_clock_time: float
    cleanup_processor_time: float
    insert_clock_time: float
    insert_processor_time: float
    update_clock_time: float
    update_processor_time: float


def setup_results_file(file: Path):
    with file.open("w") as f:
        headers = [
            "alert_count",
            "insert_clock_time",
            "insert_processor_time",
            "cleanup_clock_time",
            "cleanup_processor_time",
            "update_clock_time",
            "update_processor_time",
        ]
        f.write(",".join(headers) + "\n")


def append_results_file(file: Path, alert_count: int, measurement: Measurement) -> None:
    with file.open("a") as f:
        data = (
            alert_count,
            measurement.insert_clock_time,
            measurement.insert_processor_time,
            measurement.cleanup_clock_time,
            measurement.cleanup_processor_time,
            measurement.update_clock_time,
            measurement.update_processor_time,
        )
        f.write(",".join(map(str, data)) + "\n")


def main():
    results_file = Path("monitor_measurements.csv")
    setup_results_file(results_file)

    grafana_session = BaseUrlSession(prefix_url="http://localhost:3000/api/")
    grafana_session.auth = (USERNAME, PASSWORD)

    grafana_provider = GrafanaProvider(grafana_session)

    state = FileState(
        Path("./performance_state.json"),
        save_state=True,
        persist_untracked=False,
    )

    monitor = Monitor(
        providers=[grafana_provider],
        state=state,
    )

    cleanup(monitor)

    # alert_counts = [1]
    # on 1000 alerts my grafana setup failed on locked database
    alert_counts = [1, 3, 5, 10, 15, 20, 25, 50, 100, 200, 300, 500, 700]

    for idx, alert_count in enumerate(alert_counts):
        logger.info(f"Processing {alert_count} case ({idx + 1} / {len(alert_counts)})")

        insert_clock_spent, insert_processor_spent = run(
            monitor=monitor, alert_count=alert_count, dry_run=False
        )
        # update_clock_spent, update_processor_spent = run(
        #     monitor=monitor,
        #     alert_count=alert_count,
        #     dry_run=False,
        #     custom_label="Updated value",
        # )
        cleanup_clock_spent, cleanup_processor_spent = cleanup(monitor)

        measurement = Measurement(
            cleanup_clock_time=cleanup_clock_spent,
            cleanup_processor_time=cleanup_processor_spent,
            insert_clock_time=insert_clock_spent,
            insert_processor_time=insert_processor_spent,
            update_clock_time=0,
            update_processor_time=0,
            # update_clock_time=update_clock_spent,
            # update_processor_time=update_processor_spent,
        )

        append_results_file(results_file, alert_count, measurement)


if __name__ == "__main__":
    main()
