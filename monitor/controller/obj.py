import json
from abc import ABC, abstractmethod
from functools import partial

from pydantic import BaseModel


class MonitoringObject(BaseModel, ABC):
    @property
    @abstractmethod
    def local_id(self) -> str:
        pass

    class Config:
        json_dumps = partial(
            json.dumps,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
