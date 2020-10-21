import typing
from enum import Enum
from queue import Queue
from typing import List

import attr

from base_gui.app_logging import LOGGER
from base_gui.mac.message import Message, MESSAGE_DISTANCE_PER_TIME, ImmutableMessage


class State(Enum):
    IDLE = 0
    SENDING_DATA = 11
    # SENDING_RTS = 12
    SENDING_CTS = 13
    # SENDING_ACK = 14
    AWAITING_DATA = 21
    AWAITING_CTS = 22
    # AWAITING_ACK = 24
    RECEIVING_DATA = 31
    RECEIVING_CTS = 32
    # RECEIVING_RTS = 33
    # RECEIVING_ACK = 34


@attr.attrs(auto_attribs=True, frozen=True)
class FrozenActorState(object):
    state: State
    neighbour_messages_carriersense: typing.Tuple[ImmutableMessage]
    queued_messages: typing.Tuple[ImmutableMessage]
    in_transit_messages: typing.Tuple[ImmutableMessage]


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

    def get_frozen_state(self, actor_position) -> FrozenActorState:
        frozen_queue_items: List[ImmutableMessage] = list()
        frozen_transit_items: List[ImmutableMessage] = list()
        frozen_neighbour_items: List[ImmutableMessage] = list()
        for queued_message in self.queued_messages.queue:
            frozen_queue_items.append(queued_message.get_immutable_message())
        for in_transit_message in self.in_transit_messages.queue:
            frozen_transit_items.append(in_transit_message.get_immutable_message())
        for neighbour_message in self.get_neighbour_messages_carriersense(actor_position=actor_position):
            frozen_neighbour_items.append(neighbour_message.get_immutable_message())
        return FrozenActorState(
            state=self.state,
            queued_messages=tuple(frozen_queue_items),
            in_transit_messages=tuple(frozen_transit_items),
            neighbour_messages_carriersense=tuple(frozen_neighbour_items)
        )

    def can_transmit(self, message: Message):
        # check if message needs to be queued, dependent on own state and neighbour's state:
        # - Carrier sense blocked by looking at self.interacting_neighbours
        # - SENDING transmitting message (DATA/RTS)
        # NOT IMPLEMENTED YET - AWAITING awaiting CTS

        # Protocol check
        # else if awaiting CTS/RTS => MAC algorithm
        #   -- implement protocol check HERE --

        # Internal transmission check
        if self.queued_messages.qsize() > 0:
            return False
        elif self.in_transit_messages.qsize() > 0:
            # for message in list(self.in_transit_messages):
            last_message = self.in_transit_messages.queue[-1]
            if last_message.check_message_transmitting():
                return False

        # Carrier sense external
        return not self.check_message_carriersense(message.origin_position)

    def get_neighbour_messages_carriersense(self, actor_position):
        arriving_messages: List[Message] = list()
        for neighbour in self.neighbour_states:
            for message in neighbour.in_transit_messages.queue:
                # It would be illegal to find neighbour messages except for the ones 'arriving'
                if message.check_message_arriving(actor_position):
                    arriving_messages.append(message)
        return arriving_messages

    def check_message_carriersense(self, actor_position):
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

            # print("MSG from queue to transmit >>>", message.payload, "queue length", self.queued_messages.qsize())

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
