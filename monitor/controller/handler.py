from typing import Any, Generic, Optional, TypeVar

from abc import ABC, abstractmethod

import requests
from requests.auth import AuthBase

from monitor.controller.obj import MonitoringObject
from monitor.controller.resource import IdType, Resource

S = TypeVar("S", bound=Resource[MonitoringObject])


class ResourceHandler(Generic[S], ABC):
    # todo: add readall ???
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
