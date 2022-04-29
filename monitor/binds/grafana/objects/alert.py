from .base import GrafanaObject


class Alert(GrafanaObject):
    @property
    def local_id(self) -> str:
        pass
