from pathlib import Path
from urllib.parse import urljoin

from loguru import logger
from requests import Response, Session, HTTPError

from binds.grafana.grafana_provider import GrafanaProvider
from controller.monitor import Monitor
from controller.states import FileState
from demo.applier.grafana_minimalistic import green_fruits_bundle

from grafana_modelled_conds import get_checks as get_demo_checks

USERNAME = "admin"
PASSWORD = "admin"
DATASOURCE_UID = "PrometheusUID"


class BaseUrlSession(Session):
    def __init__(self, prefix_url=None):
        super().__init__()
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs) -> Response:
        url = urljoin(self.prefix_url, url)
        return super().request(method, url, *args, **kwargs)


def main():
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

    try:
        monitor.apply_monitoring_state(
            monitoring_objects=[
                *green_fruits_bundle(DATASOURCE_UID),
                *get_demo_checks(DATASOURCE_UID),
            ],
            # dry_run=True,
            dry_run=False,
        )
    except HTTPError as e:
        logger.debug(e.response.json())
        raise e


if __name__ == '__main__':
    main()
