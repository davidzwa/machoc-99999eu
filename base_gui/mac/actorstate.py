from enum import Enum
from typing import List

from base_gui.mac.message import Message


class State(Enum):
    IDLE = 0
    SENDING = 1
    AWAITING = 2
    RECEIVING = 3


class ActorState(object):
    def __init__(self, identifier, time):
        self.identifier = identifier
        self.time = time

        # Time until a delaying state ends, 0 if not transmitting/waiting, also 0 if receiving
        self.state_duration_time = 0
        self.state = State.IDLE
        # Flattened way to decide colliding messages
        self.inrange_neighbours: List[ActorState] = list()
        self.queued_messages: List[Message] = list()
        self.in_transit_messages: List[Message] = list()

    def handle_new_data_packet(self, message: Message):
        can_transmit = self.can_transmit(message)
        if can_transmit:
            self.in_transit_messages.append(message)
        else:
            self.queued_messages.append(message)

        if len(self.in_transit_messages) > 1:
            pass

    def can_transmit(self, message: Message):
        # check if message needs to be queued, dependent on own state and neighbour's state:
        # - Carrier sense blocked by looking at self.interacting_neighbours
        # - SENDING transmitting message (DATA/RTS)
        # NOT IMPLEMENTED YET - AWAITING awaiting CTS

        if len(self.queued_messages) > 0:
            return False
        elif len(self.in_transit_messages) > 0:
            for message in self.in_transit_messages:
                if message.check_message_transmitting():
                    return False
        # else if awaiting CTS/RTS => MAC algorithm
        #   -- implement protocol check HERE --
        return not self.check_message_arriving(message.origin_position)

    def check_message_arriving(self, actor_position):
        """
        Nice method to check whether neighbouring actors have messages which are already streaming into our position.
        """
        for neighbour in self.inrange_neighbours:
            for message in neighbour.in_transit_messages:
                # It would be illegal to find neighbour messages except for the ones 'arriving'
                if message.check_message_arriving(actor_position):
                    return True
        return False

    def progress_actorstate_time(self, time):
        # Convert time to find new distance of message: head of wave
        self.time = time

    def purge_outofrange_messages(self):
        self.in_transit_messages = [message for message in self.in_transit_messages if not message.check_message_done()]
