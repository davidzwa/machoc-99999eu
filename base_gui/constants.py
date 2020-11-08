import enum
from typing import Dict, Any

import pygame
from pygame import Vector2

# Defines both the number of checkboxes and their labels
from base_gui.mac.macstate import MacState
from base_gui.mac.messagetype import MessageType

MENU_CHECKBOX_NODELABELS_INDEX = 0
MENU_CHECKBOX_SIMTYPE_INDEX = 1
MENU_CHECKBOXES_GENERIC = (
    "Hide node labels",  # Index 1
    # "MAC 0, ROUTING 1",  # Index 0
)
MENU_CHECKBOX_MAC_AUTOPLAY = 0
MENU_CHECKBOXES_MAC = (
    "Auto-play sim",  # index 0
)
MENU_CHECKBOXES_ROUTING = (
    "ROUTING checkbox here",
)


class SimType(enum.Enum):
    MAC = 0
    ROUTING = 1

def get_pixel_meter_ratio():
    return PIXELS_PER_METER

PIXELS_PER_METER = 45  # Might become dynamic based on zoom later
SIM_MODE = SimType.MAC  # Not implemented
NAV_WIDTH = 200
BOTTOM_HEIGHT = 0
SIM_SIZE = Vector2(1200, 800)
SCREEN_SIZE = Vector2(SIM_SIZE.x + NAV_WIDTH, SIM_SIZE.y + BOTTOM_HEIGHT)
AUTOPLAY_SPEED_MS = 200  # 5 steps per second
TIMELINE_SCROLL_DEBOUNCE = 75  # minimum ticks between timeline update by LEFT/RIGHT arrows

class SimConsts(object):
    TIME_MAX_STEPS = 100
    TIME_STEP = 1

    # MAC SIMULATION PARAMETERS
    NUM_NODES_MAC = 10
    DISTANCE_SPREAD_SIGMA_MAC = 250

    WAVE_VELOCITY = 1  # meters per timestep

    PACKET_LENGTH_SPACE = 10  # meters
    JAMMING_LENGTH_SPACE = 1  # meters

    TRANSMISSION_RANGE = 20  # meters

    TRAFFIC_LOAD = 10  # Messages per timestep
    MESSAGE_ARRIVAL_PROBABILITY = TRAFFIC_LOAD / NUM_NODES_MAC  # Message chance per timestep
    assert MESSAGE_ARRIVAL_PROBABILITY <= 1

    # MAXIMAL NUMBER OF RETRANSMISSION ATTEMPTS BEFORE DROPPIING THE PACKAGE
    MAX_ATTEMPTS = 6

    STATE_COLOR_DICT: Dict[MacState, pygame.Color] = {
        MacState.IDLE: pygame.Color("gray"),
        MacState.READY_TO_TRANSMIT: pygame.Color("blue"),
        MacState.WAIT: pygame.Color("green"),
        MacState.TRANSMITTING: pygame.Color("purple"),
        MacState.JAMMING: pygame.Color("red")
    }

    # Used for legend
    STATE_DESCRIPTION_DICT: Dict[MacState, Any] = {
        MacState.IDLE: "Idle node",
        MacState.READY_TO_TRANSMIT: "Node ready to transmit",
        MacState.WAIT: "Node waiting",
        MacState.TRANSMITTING: "Node transmitting",
        MacState.JAMMING: "Node jamming"
    }

    MESSAGE_COLOR_DICT: Dict[MessageType, pygame.Color] = {
        MessageType.DATA: pygame.Color("black"),
        MessageType.CTS: pygame.Color("black"),
        MessageType.RTS: pygame.Color("black"),
        MessageType.ACK: pygame.Color("black"),
        MessageType.JAMMING: pygame.Color("red3"),
        MessageType.RETRANSMISSION: pygame.Color("blue")
    }

    WAVES_DENSITY = 2