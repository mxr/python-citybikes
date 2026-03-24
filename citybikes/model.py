from dataclasses import dataclass, field, fields
from typing import Any, cast, TypeVar

T = TypeVar("T", bound="AllowExtra")

class AllowExtra:
    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        valid_keys = {f.name for f in fields(cast(Any, cls))}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

@dataclass
class Station(AllowExtra):
    id: str
    name: str
    latitude: float
    longitude: float
    extra: dict[str, Any]
    timestamp: str
    free_bikes: int | None = None
    empty_slots: int | None = None


@dataclass
class Location:
    latitude: float
    longitude: float
    city: str
    country: str

@dataclass
class Network(AllowExtra):
    id: str
    name: str
    location: Location | dict[str, Any]
    href: str
    stations: list[Station] | list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.stations = [Station.from_dict(s) for s in self.stations]  # type: ignore[arg-type]  # TODO: Runtime data may already contain Station objects.
        if isinstance(self.location, dict):
            self.location = Location(**self.location)
