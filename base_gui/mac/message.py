from enum import Enum

import numpy as np


class MessageType(Enum):
    DATA = 0,
    CTS = 1,
    RTS = 2,
    ACK = 3


class Message(object):
    def __init__(self,
                 type: MessageType,
                 origin: np.ndarray,
                 max_range: float, prop_length: float):
        assert prop_length > 0.0
        self.prop_length: float = prop_length  # Propagation length in meters (relatable to frame length)
        self.max_range = max_range
        self.type = type
        self.origin = origin
        self.prop_distance = 0.0  # Current head of wave

    def message_travel(self, distance: float):
        self.prop_distance += distance

    def calculate_actor_collide(self, actor):
        """
        Calculate whether head of wave in range
        """
        position = actor.position
        txrx_dist = np.linalg.norm(position - self.origin)
        return txrx_dist <= self.max_range \
               and txrx_dist < self.prop_distance <= txrx_dist + self.prop_length

    def check_message_done(self):
        """
        Check if message has travelled beyond furthest point
        """
        return self.max_range < self.prop_distance + self.prop_length
