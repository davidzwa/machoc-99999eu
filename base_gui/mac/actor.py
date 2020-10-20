import uuid
from typing import List

import numpy as np

from base_gui.mac.actorstate import ActorState
from base_gui.mac.message import Message, MessageType, MESSAGE_DISTANCE_PER_TIME


class Actor(object):
    def __init__(
            self,
            identifier: str,
            position: np.ndarray,
            state=None):

        self.identifier = identifier
        self.position: np.ndarray = position
        self.neighbours: List[Actor] = list()

        self.time = None
        if state is None:
            self.state: ActorState = ActorState(identifier, self.time)
        else:
            self.state = state
        self.history: List[ActorState] = list()

    def add_neighbour(self, neighbour):
        if neighbour not in self.neighbours:
            self.neighbours.append(neighbour)

    def clear_state(self):
        self.time = None
        self.state: ActorState = ActorState(self.identifier, self.time)
        self.history = list()

    def attempt_transmission(self, max_transmission_range=100 * MESSAGE_DISTANCE_PER_TIME,
                             packet_length=25 * MESSAGE_DISTANCE_PER_TIME):
        """
        Send a DATA packet with x times the length of the most basic TIME unit
        The underlying protocol will send RTS/CTS
        """
        msg = Message(
            type=MessageType.DATA,
            prop_packet_length=packet_length,
            origin=self.position,
            payload=uuid.uuid4(),
            max_range=max_transmission_range
        )
        self.state.handle_new_data_packet(message=msg)

    def progress_time(self, new_time):
        """
        Assign new time, assume it is monotonically increasing.
        """
        assert new_time > self.time if self.time is not None else True
        self.time = new_time
