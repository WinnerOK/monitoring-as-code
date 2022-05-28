from .base import GrafanaObject


class Folder(GrafanaObject):
    title: str

    @property
    def local_id(self) -> str:
        return self.title
