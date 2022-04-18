# fixme Deprecated concept
from abc import ABC, abstractmethod
from typing import Union

from pydantic import BaseModel

ID_TYPE = Union[str, int]


class ApiEntity(BaseModel, ABC):
    """
    A class representing an entity that is used to operate with an API.
    I.e: Alert for Grafana alerting subsystem
    """

    @property
    @abstractmethod
    def id(self) -> ID_TYPE:
        pass
