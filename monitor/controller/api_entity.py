from pydantic import BaseModel
from typing import Union, Optional, TypeVar
from abc import ABC, abstractmethod

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
