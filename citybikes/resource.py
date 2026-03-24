# -*- coding: utf-8 -*-

import json
from collections.abc import Iterator
from typing import Any
from urllib.parse import urljoin


class Resource:
    uri: str | None = None

    resource_class: type["Resource"] | None = None
    resource_path: str | None = None
    resource_wrap: str | None = None

    def __init__(self, client: Any, data: dict[str, Any] | None = None) -> None:
        self.client = client
        self.url = urljoin(client.endpoint, self.uri)
        self._data = data or {}

    @property
    def data(self) -> dict[str, Any]:
        if not self.is_complete:
            self.request()
        return self._data

    @property
    def is_complete(self) -> bool:
        if not self._data:
            return False
        if self.resource_path and self.resource_path not in self._data:
            return False
        return True

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __iter__(self) -> Iterator["Resource"]:
        things = self.get_resource()
        for x in things:
            if self.resource_class is None:
                raise TypeError("resource_class must be set")
            yield self.resource_class(self.client, x)

    def __len__(self) -> int:
        return len(self.get_resource())

    def __delitem__(self, key: str) -> None:
        del self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def request(self, _path: str | None = None, **kwargs: Any) -> None:
        kwargs['method'] = 'GET'
        data = self.client.request(urljoin(self.url, _path), **kwargs).json()
        if self.resource_wrap:
            data = data[self.resource_wrap]
        self._data.update(data)

    def get_resource(self) -> list[dict[str, Any]]:
        if self.resource_path is None:
            raise TypeError("resource_path must be set")
        resource = self.get(self.resource_path)
        if not isinstance(resource, list):
            raise TypeError("resource data must be a list")
        return resource

    def __repr__(self) -> str:
        return repr(self.data)


class AbstractResource(Resource):
    def __init__(self, client: Any, parent: Resource) -> None:
        super(AbstractResource, self).__init__(client, parent.data)
        self.parent = parent

    def request(self, *args: Any, **kwargs: Any) -> None:
        return self.parent.request(*args, **kwargs)


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        return o.data
