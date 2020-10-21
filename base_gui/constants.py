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

PIXELS_PER_METER = 10 # Might become dynamic based on zoom later
SIM_MODE = SimType.MAC  # Not implemented
NAV_WIDTH = 200
BOTTOM_HEIGHT = 0
SIM_SIZE = Vector2(800, 800)
SCREEN_SIZE = Vector2(SIM_SIZE.x + NAV_WIDTH, SIM_SIZE.y + BOTTOM_HEIGHT)

class SimConsts(object):
    TIME_MAX_STEPS = 500
    TIME_STEP = 1

    # MAC SIMULATION PARAMETERS
    NUM_NODES_MAC = 7
    DISTANCE_SPREAD_SIGMA_MAC = 250
    PACKET_LENGTH_SPACE = 3
    TRANSMISSION_RANGE = 30
    TRANSMISSION_CHANCE = 0.03
    WAVES_DENSITY = 5

    # ROUTING SIMULATION PARAMETERS
    NUM_NODES_ROUTING = 5
    DISTANCE_SPREAD_SIGMA_ROUTING = 30
