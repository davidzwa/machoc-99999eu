import enum

from pygame import Vector2

# Defines both the number of checkboxes and their labels
MENU_CHECKBOX_SIMTYPE_INDEX = 0
MENU_CHECKBOX_NODELABELS_INDEX = 1
MENU_CHECKBOXES_GENERIC = (
    "MAC 0, ROUTING 1",  # Index 0
    "Hide node labels",  # Index 1
)
MENU_CHECKBOXES_MAC = (
    "MAC checkbox here",
)
MENU_CHECKBOXES_ROUTING = (
    "ROUTING checkbox here",
)


class SimType(enum.Enum):
    MAC = 0
    ROUTING = 1

PIXELS_PER_METER = 20 # Might become dynamic based on zoom later
SIM_MODE = SimType.MAC  # Not implemented
NAV_WIDTH = 200
BOTTOM_HEIGHT = 0
SIM_SIZE = Vector2(800, 800)
SCREEN_SIZE = Vector2(SIM_SIZE.x + NAV_WIDTH, SIM_SIZE.y + BOTTOM_HEIGHT)

class SimConsts(object):
    # MAC SIMULATION PARAMETERS
    NUM_NODES_MAC = 10
    DISTANCE_SPREAD_SIGMA_MAC = 20

    # ROUTING SIMULATION PARAMETERS
    NUM_NODES_ROUTING = 5
    DISTANCE_SPREAD_SIGMA_ROUTING = 30
