from enum import Enum

class MessageType(Enum):
    DATA = 0,
    CTS = 1,
    RTS = 2,
    ACK = 3,
    JAMMING = 5,
    RETRANSMISSION = 6

