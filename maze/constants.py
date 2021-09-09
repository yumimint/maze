import enum

from .util import hsv2rgb


class FieldValue(enum.IntEnum):
    SPACE = 0
    WALL = 1
    MARK = 2
    ROUTE = 3
    ROUTE2 = 4
    VISITED = 128
    VISITED0 = VISITED + 0
    VISITED1 = VISITED + 1
    VISITED2 = VISITED + 2
    VISITED3 = VISITED + 3


DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]


COLORMAP = {
    FieldValue.SPACE: hsv2rgb(0, 0, 100),
    FieldValue.WALL: (0, 0, 0),
    FieldValue.MARK: hsv2rgb(0, 0.5, 100),
    FieldValue.ROUTE: hsv2rgb(1 / 3, 0.6, 140),
    FieldValue.ROUTE2: hsv2rgb(0, 0.6, 140),
    FieldValue.VISITED0: hsv2rgb(0 / 4, 0.8, 200),
    FieldValue.VISITED1: hsv2rgb(1 / 4, 0.8, 200),
    FieldValue.VISITED2: hsv2rgb(2 / 4, 0.8, 200),
    FieldValue.VISITED3: hsv2rgb(3 / 4, 0.8, 200),
}
