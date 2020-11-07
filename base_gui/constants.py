import enum
from typing import Dict

import pygame
from pygame import Vector2

# Defines both the number of checkboxes and their labels
from base_gui.mac.macstate import MacState
from base_gui.mac.messagetype import MessageType

MENU_CHECKBOX_SIMTYPE_INDEX = 0
MENU_CHECKBOX_NODELABELS_INDEX = 1
MENU_CHECKBOXES_GENERIC = (
    "MAC 0, ROUTING 1",  # Index 0
    "Hide node labels",  # Index 1
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


PIXELS_PER_METER = 10  # Might become dynamic based on zoom later
SIM_MODE = SimType.MAC  # Not implemented
NAV_WIDTH = 200
BOTTOM_HEIGHT = 0
SIM_SIZE = Vector2(1200, 800)
SCREEN_SIZE = Vector2(SIM_SIZE.x + NAV_WIDTH, SIM_SIZE.y + BOTTOM_HEIGHT)


class SimConsts(object):
    TIME_MAX_STEPS = 1000
    TIME_STEP = 1

    # MAC SIMULATION PARAMETERS
    NUM_NODES_MAC = 10
    DISTANCE_SPREAD_SIGMA_MAC = 250

    WAVE_VELOCITY = 1  # meters per timestep

    PACKET_LENGTH_SPACE = 10  # meters
    JAMMING_LENGTH_SPACE = 1  # meters

    TRANSMISSION_RANGE = 20  # meters

    TRANSMISSION_CHANCE = 0.01  # Transmission chance per timestep



    # MAXIMAL NUMBER OF RETRANSMISSION ATTEMPTS BEFORE DROPPIING THE PACKAGE
    MAX_ATTEMPTS = 6

    STATE_COLOR_DICT: Dict[MacState, pygame.Color] = {
        MacState.IDLE: pygame.Color("gray"),
        MacState.READY_TO_TRANSMIT: pygame.Color("blue"),
        MacState.WAIT: pygame.Color("green"),
        MacState.TRANSMITTING: pygame.Color("purple"),
        MacState.JAMMING: pygame.Color("red")
    }

    MESSAGE_COLOR_DICT: Dict[MessageType, pygame.Color] = {
        MessageType.DATA: pygame.Color("black"),
        MessageType.CTS: pygame.Color("black"),
        MessageType.RTS: pygame.Color("black"),
        MessageType.ACK: pygame.Color("black"),
        MessageType.JAMMING: pygame.Color("red3"),
        MessageType.RETRANSMISSION: pygame.Color("blue")
    }
