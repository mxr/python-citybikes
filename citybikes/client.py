# -*- coding: utf-8 -*-
from typing import Any

import requests

from citybikes import __version__ as _version
from citybikes.resource import AbstractResource, Resource
from citybikes.utils import dist_sort


class Client(object):

    DEFAULT_ENDPOINT = 'https://api.citybik.es/'
    USER_AGENT = 'python-citybikes/{version}'.format(version=_version)

    def __init__(self, endpoint: str | None = None, headers: dict[str, str] | None = None) -> None:
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT
        headers = headers or {}

        if "user-agent" not in (k.lower() for k in headers):
            headers["user-agent"] = self.USER_AGENT

        self.session = requests.session()
        self.session.headers.update(headers)
        self.networks = Networks(self)

    def request(self, url: str, **kwargs: Any) -> requests.Response:
        kwargs['url'] = url
        return self.session.request(**kwargs)


class Network(Resource):
    uri = '/v2/networks/{uid}'
    resource_wrap = 'network'

    def __init__(self, client: Client, data: dict[str, Any] | None = None, uid: str | None = None) -> None:
        self.uri = data['href'] if data else self.uri.format(uid=uid)
        super(Network, self).__init__(client, data=data)
        self.stations = Stations(client, parent=self)


class Networks(Resource):
    uri = 'v2/networks'
    resource_class = Network
    resource_path = 'networks'

    def near(self, lat: float, lng: float) -> list[tuple[Resource, float]]:
        def getter(network: Resource) -> tuple[float, float]:
            return (network['location']['latitude'],
                    network['location']['longitude'])
        return dist_sort([lat, lng], list(iter(self)), getter)


class Station(Resource):
    pass


class Stations(AbstractResource):
    resource_class = Station
    resource_path = 'stations'

    def near(self, lat: float, lng: float) -> list[tuple[Resource, float]]:
        def getter(station: Resource) -> tuple[float, float]:
            return (station['latitude'], station['longitude'])
        return dist_sort([lat, lng], list(iter(self)), getter)
