import uuid
from typing import Any

import attr
import numpy as np

from base_gui.constants import SimConsts
from base_gui.mac.messagetype import MessageType


@attr.attrs(auto_attribs=True, frozen=True)
class ImmutableMessage(object):
    """
    Freeze a message to save it to history
    """
    prop_packet_length: float = attr.attrib()
    origin_position: np.ndarray
    # Any metadata required for proper functioning of the MAC layer. For example: RTS/CTS+data length window
    packet_id: uuid.UUID
    max_range: float
    type: MessageType
    prop_distance: float
    retransmission_parent: uuid.UUID
    attempt_count: int


class Message(object):
    """
    A multi-functional data object tied to the transmitting actor, moment transmission and a propagation distance.
    Conclusion: it can be visualized as a donut wave-front, whilst also carrying MAC-layer metadata.
    """

    def __init__(self,
                 type: MessageType,
                 prop_packet_length: float,
                 origin: np.ndarray,
                 packet_id: Any,
                 max_range: float,
                 retransmission_parent: Any,
                 attempt_count: int,
                 wave_velocity=SimConsts.WAVE_VELOCITY):

        # Propagation time converted to travel length (relatable to frame length)
        assert prop_packet_length > 0.0
        self.prop_packet_length: float = prop_packet_length
        # Any metadata required for proper functioning of the MAC layer. For example: RTS/CTS+data length window
        self.packet_id = packet_id
        self.max_range = max_range
        self.type = type
        self.origin_position = origin
        self.prop_distance = 0.0  # Current head of wave, dynamic
        self.retransmission_parent = retransmission_parent
        self.attempt_count = attempt_count

        self.wave_velocity = wave_velocity

    def message_travel(self, delta_distance):
        self.prop_distance += delta_distance

    def get_immutable_message(self):
        return ImmutableMessage(
            self.prop_packet_length,
            self.origin_position,
            self.packet_id,
            self.max_range,
            self.type,
            self.prop_distance,
            self.retransmission_parent,
            self.attempt_count
        )

    def get_distance_travelled(self):
        return self.prop_distance

    def check_tail_beyond_receiver(self, actor_position):
        """
        Calculate whether head of wave + propagation length is beyond a receiving actor.
        If so: could trigger RX scenario, if not received already by that actor.
        """
        txrx_dist = np.linalg.norm(actor_position - self.origin_position)
        return self.prop_distance > txrx_dist + self.prop_packet_length

    def check_message_transmitting(self):
        """
        Check if message is still 'leaving the transmitter'
        """
        return self.prop_distance < self.prop_packet_length

    def check_message_arriving(self, actor_position):
        """
        Check if message is 'entering a receiver' (but has not moved beyond)
        Note: handy as carrier check.
        """
        txrx_dist = np.linalg.norm(actor_position - self.origin_position)
        return not self.prop_distance > txrx_dist + self.prop_packet_length and self.prop_distance > txrx_dist

    def check_message_done(self):
        """
        Check if message has travelled beyond furthest point (max range)
        """
        return self.max_range < self.prop_distance

    def cut_off_message(self):
        """
        Stop transmitting new parts of the message, reducing the length to what was already in the air
        """
        assert self.check_message_transmitting()
        self.prop_packet_length = self.prop_distance

    def propagate(self, delta_time_step) -> int:
        self.prop_distance += delta_time_step * self.wave_velocity

        if self.check_message_done():
            overshot = self.prop_distance - self.max_range
            if overshot > self.prop_packet_length:  # entire message is out of range, return 1 to purge message
                return 1
            else:
                self.prop_packet_length -= overshot
                self.prop_distance = self.max_range

        return 0

        # outofrange_messages = list()
        # for message in self.in_transit_messages.queue:
        #      message.prop_distance += self.time_step * MESSAGE_DISTANCE_PER_TIME
        #     if message.check_message_done():
        #         outofrange_messages.append(message)
        # # Convert time to find new distance of message: head of wave
        # self.time += self.time_step
        # self.purge_outofrange_messages(outofrange_messages)  # TODO purge + cutoff

    # def __del__(self):
    #     pass
    # print("Im losing it.")
