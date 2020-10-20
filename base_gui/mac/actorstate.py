from enum import Enum
from typing import List

from base_gui.mac.message import Message


class State(Enum):
    IDLE = 0
    AWAITING = 1
    RECEIVING = 2
    SENDING = 3


class ActorState(object):
    def __init__(self, identifier, time):
        self.identifier = identifier
        self.time = time

        # Time until a delaying state ends, 0 if not transmitting/waiting, also 0 if receiving
        self.state_duration_time = 0
        self.state = State.IDLE
        # Flattened way to decide collisions, but only if these neighbours messages are in ARRIVAL state
        self.interacting_neighbours: List = list()
        self.in_transit_messages: List[Message] = list()

    def send_message(self, message: Message):
        self.in_transit_messages.append(message)

    def check_dead_messages(self):
        self.in_transit_messages = [message for message in self.in_transit_messages if not message.check_message_done()]
        for message in self.in_transit_messages:
            message.check_message_done()
