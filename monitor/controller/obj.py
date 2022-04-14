from abc import ABC, abstractmethod

from pydantic import BaseModel


class MonitoringObject(BaseModel, ABC):
    @property
    @abstractmethod
    def local_id(self) -> str:
        pass
