from pydantic import Field

from monitor.controller.resource import Resource


class Folder(Resource):
    uid: str = Field(..., include=True)
    title: str = Field(..., include=True)

    @property
    def _local_id(self) -> str:
        return self.uid
