import random
import typing
import uuid
from enum import Enum
from queue import Queue
from typing import List

import attr

from base_gui.app_logging import LOGGER
from base_gui.constants import SimConsts
from base_gui.mac.macstate import MacState
from base_gui.mac.message import Message, ImmutableMessage, MessageType


class CarrierSenseState(Enum):
    IDLE = 0
    QUEUED = 1
    TRANSMITTING = 2
    RECEIVING = 3


@attr.attrs(auto_attribs=True, frozen=True)
class FrozenActorState(object):
    macState: MacState
    identifier: str
    neighbour_messages_carriersense: typing.Tuple[ImmutableMessage]
    queued_messages: typing.Tuple[ImmutableMessage]
    in_transit_messages: typing.Tuple[ImmutableMessage]

    num_successful_transmissions: int
    num_transmission_attempts: int
    num_collisions: int
    num_dropped_messages: int

    transmission_times: list
    num_messages: int


class ActorState(object):
    def __init__(self, identifier, time, position,
                 transmission_range=SimConsts.TRANSMISSION_RANGE,
                 data_packet_length=SimConsts.PACKET_LENGTH_SPACE,
                 jamming_packet_length=SimConsts.JAMMING_LENGTH_SPACE,
                 time_step=SimConsts.TIME_STEP,
                 max_attempts=SimConsts.MAX_ATTEMPTS):

        self.identifier = identifier
        self.time = time

        # Time until a delaying state ends, 0 if not transmitting/waiting, also 0 if receiving
        self.state_duration_time = 0
        self.state = MacState.IDLE
        # Flattened way to decide colliding messages
        self.neighbour_states: List[ActorState] = list()
        self.queued_messages: Queue[Message] = Queue()
        self.in_transit_messages: Queue[Message] = Queue()

        self.position = position

        self.max_transmission_range = transmission_range
        self.data_packet_length = data_packet_length
        self.jamming_packet_length = jamming_packet_length

        self.time_step = time_step

        self.max_attempts = max_attempts
        self.wait_time = 0

        self.num_successful_transmissions = 0
        self.num_transmission_attempts = 0
        self.num_collisions = 0
        self.num_dropped_messages = 0
        self.num_messages = 0

        self.transmission_times = list()

        self.drop_message = False

    def add_neighbour_state(self, state: 'ActorState'):
        if state not in self.neighbour_states:
            self.neighbour_states.append(state)

    def get_frozen_state(self) -> FrozenActorState:
        frozen_queue_items: List[ImmutableMessage] = list()
        frozen_transit_items: List[ImmutableMessage] = list()
        frozen_neighbour_items: List[ImmutableMessage] = list()
        for queued_message in self.queued_messages.queue:
            frozen_queue_items.append(queued_message.get_immutable_message())
        for in_transit_message in self.in_transit_messages.queue:
            frozen_transit_items.append(in_transit_message.get_immutable_message())
        for neighbour_message in self.get_neighbour_messages_carriersense():
            frozen_neighbour_items.append(neighbour_message.get_immutable_message())
        return FrozenActorState(
            macState=self.state,
            identifier=self.identifier,
            queued_messages=tuple(frozen_queue_items),
            in_transit_messages=tuple(frozen_transit_items),
            neighbour_messages_carriersense=tuple(frozen_neighbour_items),
            num_collisions=self.num_collisions,
            num_dropped_messages=self.num_dropped_messages,
            num_successful_transmissions=self.num_successful_transmissions,
            num_transmission_attempts=self.num_transmission_attempts,
            num_messages=self.num_messages,
            transmission_times=self.transmission_times
        )

    def can_transmit(self, message: Message) -> CarrierSenseState:
        # check if message needs to be queued, dependent on own state and neighbour's state:
        # - Carrier sense blocked by looking at self.interacting_neighbours
        # - SENDING transmitting message (DATA/RTS)
        # NOT IMPLEMENTED YET - AWAITING awaiting CTS

        # Protocol check
        # else if awaiting CTS/RTS => MAC algorithm
        #   -- implement protocol check HERE --

        # Internal transmission check
        if self.queued_messages.qsize() > 0:
            return CarrierSenseState.QUEUED
        elif self.in_transit_messages.qsize() > 0:
            # for message in list(self.in_transit_messages):
            last_message = self.in_transit_messages.queue[-1]
            if last_message.check_message_transmitting():
                return CarrierSenseState.TRANSMITTING

        # Carrier sense external
        carrier_sense_free = not self.any_neighbour_message_arriving(message.origin_position)
        if carrier_sense_free:
            return CarrierSenseState.IDLE
        else:
            return CarrierSenseState.RECEIVING

    def get_neighbour_messages_carriersense(self):
        arriving_messages: List[Message] = list()
        for neighbour in self.neighbour_states:
            for message in neighbour.in_transit_messages.queue:
                # It would be illegal to find neighbour messages except for the ones 'arriving'
                if message.check_message_arriving(self.position):
                    arriving_messages.append(message)
        return arriving_messages

    def any_neighbour_message_arriving(self):
        """
        Nice method to check whether neighbouring actors have messages which are already streaming into our position.
        """
        # TODO DO BETTER, very expensive (hashmap)
        for neighbour in self.neighbour_states:
            for message in neighbour.in_transit_messages.queue:
                # It would be illegal to find neighbour messages except for the ones 'arriving'
                if message.check_message_arriving(self.position):
                    return True
        return False

    def progress_actorstate_time(self, new_message: bool) -> typing.Any:

        if new_message:
            self.new_arrival()
            self.num_messages += 1

        # mac protocol FSM
        next_state = self.state
        if self.state == MacState.IDLE:
            if self.queued_messages.qsize() > 0:
                next_state = MacState.READY_TO_TRANSMIT

        elif self.state == MacState.READY_TO_TRANSMIT:
            if not self.any_neighbour_message_arriving():
                self.in_transit_messages.put(self.queued_messages.get())
                self.num_transmission_attempts += 1
                next_state = MacState.TRANSMITTING

        elif self.state == MacState.TRANSMITTING:
            current_message = self.in_transit_messages.queue[-1]
            if not current_message.check_message_transmitting():  # check if the message that is being transmitted has left the antenna
                self.num_successful_transmissions += 1

                transmission_time = self.time - current_message.original_start_time
                self.transmission_times.append(transmission_time)

                if self.queued_messages.qsize() > 0:
                    next_state = MacState.READY_TO_TRANSMIT
                else:
                    next_state = MacState.IDLE

            elif self.any_neighbour_message_arriving():  # Collision detected
                self.num_collisions += 1
                current_message.cut_off_message()
                if current_message.attempt_count > self.max_attempts:  # retransmission attempt limit
                    self.drop_message = True
                else:
                    self.queue_retransmission(current_message)
                    self.drop_message = False

                self.jamming_message()
                next_state = MacState.JAMMING

        elif self.state == MacState.JAMMING:
            current_message = self.in_transit_messages.queue[-1]
            if not current_message.check_message_transmitting():  # check if the message that is being transmitted has left the antenna

                if self.drop_message:
                    self.num_dropped_messages += 1
                    self.drop_message = False
                    if self.queued_messages.qsize() > 0:
                        next_state = MacState.READY_TO_TRANSMIT
                    else:
                        next_state = MacState.IDLE
                else:

                    self.wait_time = self.random_exponential_backoff(self.queued_messages.queue[0])
                    next_state = MacState.WAIT

        elif self.state == MacState.WAIT:
            self.wait_time -= 1
            if self.wait_time <= 0:
                next_state = MacState.READY_TO_TRANSMIT

        self.state = next_state
        self.time += self.time_step

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

    def new_arrival(self):
        msg = Message(
            type=MessageType.DATA,
            prop_packet_length=self.data_packet_length,
            origin=self.position,
            packet_id=uuid.uuid4(),
            max_range=self.max_transmission_range,
            retransmission_parent=0,
            attempt_count=1,
            original_start_time=self.time
        )
        self.queued_messages.put(msg)

    def jamming_message(self):
        # place jamming message on the antenna

        msg = Message(
            type=MessageType.JAMMING,
            prop_packet_length=self.jamming_packet_length,
            origin=self.position,
            packet_id=uuid.uuid4(),
            max_range=self.max_transmission_range,
            retransmission_parent=0,
            attempt_count=1,
            original_start_time=self.time

        )
        self.in_transit_messages.put(msg)

    def queue_retransmission(self, message):

        msg = Message(
            type=MessageType.RETRANSMISSION,
            prop_packet_length=self.data_packet_length,
            origin=self.position,
            packet_id=uuid.uuid4(),
            max_range=self.max_transmission_range,
            retransmission_parent=message.packet_id,
            attempt_count=message.attempt_count + 1,
            original_start_time=message.original_start_time
        )
        self.queued_messages.queue.appendleft(msg)

    def random_exponential_backoff(self, message) -> int:
        min_wait_time = 1

        if message.attempt_count <= 6:
            max_wait_time = pow(2, (2 + message.attempt_count)) - 1
        else:
            max_wait_time = 255

        wait_time = random.randint(min_wait_time, max_wait_time)

        return wait_time

    def prop_messages(self):
        # propagate messages

        outofrange_messages = list()
        for message in self.in_transit_messages.queue:
            if message.propagate(self.time_step):
                outofrange_messages.append(message)

        self.purge_outofrange_messages(outofrange_messages)
