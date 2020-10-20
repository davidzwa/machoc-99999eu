from enum import Enum
from typing import Any

import numpy as np

MESSAGE_DISTANCE_PER_TIME = 1.0 # One distance unit per time unit

class MessageType(Enum):
    DATA = 0,
    CTS = 1,
    RTS = 2,
    ACK = 3


class Message(object):
    """
    A multi-functional data object tied to the transmitting actor, moment transmission and a propagation distance.
    Conclusion: it can be visualized as a donut wave-front, whilst also carrying MAC-layer metadata.
    """

    def __init__(self,
                 type: MessageType,
                 prop_packet_length: float,
                 origin: np.ndarray,
                 payload: Any,
                 max_range: float):
        # Propagation time converted to travel length (relatable to frame length)
        assert prop_packet_length > 0.0
        self.prop_packet_length: float = prop_packet_length
        # Any metadata required for proper functioning of the MAC layer. For example: RTS/CTS+data length window
        self.payload = payload
        self.max_range = max_range
        self.type = type
        self.origin_position = origin
        self.prop_distance = 0.0  # Current head of wave, dynamic

    def message_travel(self, delta_distance):
        self.prop_distance += delta_distance

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
        return self.max_range < self.prop_distance + self.prop_packet_length

    # def __del__(self):
    #     pass
        # print("Im losing it.")