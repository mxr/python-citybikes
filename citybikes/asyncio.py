from typing import Any, cast, Generic, TypeVar
from urllib.parse import urljoin

import aiohttp

from citybikes import __version__ as _version
import citybikes.model as model
from citybikes.utils import dist_sort

T = TypeVar("T")


class Resource(Generic[T]):
    uri: str | None = None
    _data: dict[str, Any] | None = None
    _repr: T | None = None

    def __init__(self, client: "Client", _data: dict[str, Any] | None = None) -> None:
        self.client = client
        self._data = _data

    async def fetch(self, **kwargs: Any) -> T:
        self._data = await self.client.request(url=self.url, **kwargs)
        self._repr = self.parse(self._data)
        return self._repr

    def parse(self, data: dict[str, Any]) -> T:
        return cast(T, data)

    @property
    def url(self) -> str:
        return urljoin(self.client.endpoint, self.uri)

    def __getattr__(self, key: str) -> Any:
        # TODO: This should check for None before dereferencing _repr.
        return getattr(cast(T, self._repr), key)


class Networks(Resource[list[model.Network]]):
    uri = '/v2/networks'

    def parse(self, data: dict[str, Any]) -> list[model.Network]:
        return [model.Network.from_dict(n) for n in data['networks']]

    def near(self, lat: float, lng: float) -> list[tuple[model.Network, float]]:
        def getter(network: model.Network) -> tuple[float, float]:
            return (cast(model.Location, network.location).latitude, cast(model.Location, network.location).longitude)
        # TODO: This should check for None before dereferencing _repr.
        return dist_sort([lat, lng], cast(list[model.Network], self._repr), getter)


class Network(Resource[model.Network]):
    uri = '/v2/networks/{uid}'

    def __init__(self, *args: Any, uid: str, **kwargs: Any) -> None:
        self.uid = uid
        super().__init__(*args, **kwargs)

    @property
    def url(self) -> str:
        return urljoin(self.client.endpoint, self.uri.format(uid=self.uid))

    def parse(self, data: dict[str, Any]) -> model.Network:
        return model.Network.from_dict(data['network'])

    def near(self, lat: float, lng: float) -> list[tuple[model.Station, float]]:
        def getter(station: model.Station) -> tuple[float, float]:
            return (station.latitude, station.longitude)
        # TODO: This should check for None before dereferencing _repr.
        return dist_sort([lat, lng], cast(list[model.Station], cast(model.Network, self._repr).stations), getter)


class Client:
    DEFAULT_ENDPOINT = "https://api.citybik.es/"
    USER_AGENT = 'python-citybikes/{version}'.format(version=_version)


    _networks_list: Networks | None = None
    _networks: dict[str, Network]

    def __init__(self, endpoint: str | None = None, headers: dict[str, str] | None = None, user_agent: str | None = None, **kwargs: Any) -> None:
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT
        headers = headers or {}
        headers.setdefault("user-agent", user_agent or Client.USER_AGENT)
        self.session = aiohttp.ClientSession(headers=headers, **kwargs)
        self._networks = {}

    async def request(self, url: str, method: str = "GET", **kwargs: Any) -> dict[str, Any]:
        async with self.session.request(method, url, **kwargs) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def close(self) -> None:
        await self.session.close()

    @property
    def networks(self) -> Networks:
        """ Singleton networks """
        if not self._networks_list:
            self._networks_list = Networks(self)
        return self._networks_list

    def network(self, uid: str) -> Network:
        """ Singleton network """
        if uid not in self._networks:
            self._networks[uid] = Network(self, uid=uid)
        return self._networks[uid]
