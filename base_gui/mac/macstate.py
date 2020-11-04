from enum import Enum


class MacState(Enum):
    IDLE = 0
    READY_TO_TRANSMIT = 2
    TRANSMITTING = 3
    WAIT = 4
    JAMMING = 5
