from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Optional

import requests
from pydantic import HttpUrl
from requests.auth import AuthBase

from monitor.controller.resource import Resource, IdType

T = TypeVar("T", bound=Resource)


class ResourceHandler(Generic[T], ABC):
    # todo: add readall ???
    @abstractmethod
    def read(self, resource_id: IdType) -> T:
        pass

    @abstractmethod
    def create(self, resource: T) -> T:
        pass

    @abstractmethod
    def update(self, resource: T) -> T:
        pass

    @abstractmethod
    def delete(self, resource_id: IdType) -> None:
        pass


class HttpApiResourceHandler(ResourceHandler[T], ABC):
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
        self,
        method: str,
        url: str,
        query: Optional[dict[str, Any]] = None
    ) -> requests.Response:
        # todo: add retries, timeout
        return self.session.request(
            method=method,
            url=self._base_url + url,
            data=query,
        )
