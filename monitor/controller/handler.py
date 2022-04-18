from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

import requests
from requests.auth import AuthBase

from .obj import MonitoringObject
from .resource import IdType, Resource

S = TypeVar("S", bound=Resource[MonitoringObject])

# fixme: better inject requests.Session
class ResourceHandler(Generic[S], ABC):
    # todo: add readall ??? No for now!!!
    @abstractmethod
    def read(self, resource_id: IdType) -> Optional[S]:
        pass

    @abstractmethod
    def create(self, resource: S) -> tuple[S, IdType]:
        pass

    @abstractmethod
    def update(self, resource: S) -> S:
        pass

    @abstractmethod
    def delete(self, resource_id: IdType) -> None:
        pass


class HttpApiResourceHandler(ResourceHandler[S], ABC):
    def __init__(
        self,
        base_url: str,
        extra_headers: dict[str, str],
        auth: Optional[AuthBase] = None,
    ):
        self._base_url = base_url

        self.session = requests.Session()
        self.session.headers.update(extra_headers)
        if auth:
            self.session.auth = auth

    def call_api(
        self, method: str, url: str, **request_kwargs: Any
    ) -> requests.Response:
        # todo: add retries, timeout
        return self.session.request(
            method=method,
            url=self._base_url + url,
            **request_kwargs,
        )
