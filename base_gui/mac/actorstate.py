from enum import Enum
from queue import Queue
from typing import List

from base_gui.app_logging import LOGGER
from base_gui.mac.message import Message, MESSAGE_DISTANCE_PER_TIME


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
        self.neighbour_states: List[ActorState] = list()
        self.queued_messages: Queue[Message] = Queue()
        self.in_transit_messages: Queue[Message] = Queue()

    def add_neighbour_state(self, state: 'ActorState'):
        if state not in self.neighbour_states:
            self.neighbour_states.append(state)

    def handle_new_data_packet(self, message: Message):
        can_transmit = self.can_transmit(message)
        if can_transmit:
            self.in_transit_messages.put(message)
        else:
            self.queued_messages.put(message)

    def can_transmit(self, message: Message):
        # check if message needs to be queued, dependent on own state and neighbour's state:
        # - Carrier sense blocked by looking at self.interacting_neighbours
        # - SENDING transmitting message (DATA/RTS)
        # NOT IMPLEMENTED YET - AWAITING awaiting CTS

        if self.queued_messages.qsize() > 0:
            return False
        elif self.in_transit_messages.qsize() > 0:
            # for message in list(self.in_transit_messages):
            last_message = self.in_transit_messages.queue[-1]
            if last_message.check_message_transmitting():
                return False
        # else if awaiting CTS/RTS => MAC algorithm
        #   -- implement protocol check HERE --
        return not self.check_message_arriving(message.origin_position)

    def check_message_arriving(self, actor_position):
        """
        Nice method to check whether neighbouring actors have messages which are already streaming into our position.
        """
        for neighbour in self.neighbour_states:
            for message in neighbour.in_transit_messages.queue:
                # It would be illegal to find neighbour messages except for the ones 'arriving'
                if message.check_message_arriving(actor_position):
                    return True
        return False

    def progress_actorstate_time(self, delta_time):
        outofrange_messages = list()
        for message in self.in_transit_messages.queue:
            message.prop_distance += delta_time / MESSAGE_DISTANCE_PER_TIME
            if message.check_message_done():
                outofrange_messages.append(message)
        # Convert time to find new distance of message: head of wave
        self.time += delta_time
        self.purge_outofrange_messages(outofrange_messages)
        if self.queued_messages.qsize() > 0 and self.check_message_transmitting() == 0:
            length_before = self.queued_messages.qsize()
            message = self.queued_messages.get()
            self.in_transit_messages.put(message)
            length_after = self.queued_messages.qsize()
            assert length_before is length_after + 1

            print("MSG from queue to transmit >>>", message.payload, "queue length", self.queued_messages.qsize())

    def check_message_transmitting(self):
        transmitting = 0

        # Provide sanity check
        for message in self.in_transit_messages.queue:
            if message.check_message_transmitting():
                transmitting += 1
        assert transmitting <= 1  # Otherwise illegal state

        return transmitting

    def purge_outofrange_messages(self, done_messages):
        for message in done_messages:
            LOGGER.debug("Deleted message at time {} with prop. distance {} [m].".format(self.time,
                                                                                         message.get_distance_travelled()))
            self.in_transit_messages.queue.remove(message)
