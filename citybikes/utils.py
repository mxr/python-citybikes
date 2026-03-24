from math import hypot
from collections.abc import Callable, Sequence
from typing import TypeVar

Coordinate = Sequence[float]
T = TypeVar("T")

def distance(xy: Coordinate, xy2: Coordinate) -> float:
    """ Gets euclidian distance between two pairs of points (x, y)
    :param xy: pair (x, y)
    :param xy2: pair (x, y)
    :return: float

    """
    return hypot(xy[0] - xy2[0], xy[1] - xy2[1])


def dist_sort(xy: Coordinate, locations: list[T] | tuple[T, ...], getter: Callable[[T], Coordinate]) -> list[tuple[T, float]]:
    """ Sorts a list of objects by distance to x, y
    :param xy: pair (x, y)
    :param locations: list of things to sort
    :param getter: function(location) must return pair (x, y)
    :return: list of locations sorted by distance to x, y

    """
    return sorted([(loc, distance(xy, getter(loc))) for loc in locations], key=lambda locdst: locdst[1])
