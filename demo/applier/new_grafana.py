from pathlib import Path
from urllib.parse import urljoin

from binds.grafana.grafana_provider import GrafanaProvider
from binds.grafana.objects import Folder
from controller.monitor import Monitor
from controller.states import FileState
from requests import Session

USERNAME = "admin"
PASSWORD = "admin"


class BaseUrlSession(Session):
    def __init__(self, prefix_url=None):
        super().__init__()
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        return super().request(method, url, *args, **kwargs)


grafana_session = BaseUrlSession(prefix_url="http://localhost:3000/api/")
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

folder_foo = Folder(title="foo")
folder_bar = Folder(title="bar")

monitor.apply_monitoring_state(
    monitoring_objects=[folder_foo, folder_bar],
    # dry_run=True,
    dry_run=False,
)
