import enum

from pygame import Vector2


class SimType(enum.Enum):
    MAC = 1
    ROUTING = 2

MENU_CHECKBOXES = ("Display node labels", "MAC (true), ROUTING (false)")

SIM_MODE = SimType.MAC
NAV_WIDTH = 200
BOTTOM_HEIGHT = 0
SIM_SIZE = Vector2(800, 800)
SCREEN_SIZE = Vector2(SIM_SIZE.x + NAV_WIDTH, SIM_SIZE.y + BOTTOM_HEIGHT)

NUM_NODES = 10
DISTANCE_SPREAD_SIGMA = 20
