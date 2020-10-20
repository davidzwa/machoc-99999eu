from typing import List

import numpy as np

from base_gui.mac.actorstate import ActorState


class Actor(object):
    def __init__(
            self,
            identifier: str, tx_rate: float,
            position: np.ndarray,
            time: int = 0, state=None):
        assert tx_rate <= 1.0

        self.identifier = identifier
        self.tx_rate = tx_rate
        self.position: np.ndarray = position
        self.neighbours: List[Actor] = list()

        self.time = time
        if state is None:
            self.state: ActorState = ActorState(identifier, time)
        self.history: List[ActorState] = list()

    def add_neighbour(self, neighbour):
        if neighbour not in self.neighbours:
            self.neighbours.append(neighbour)

    def clear_state(self):
        self.state: ActorState = ActorState(self.identifier, self.time)
        self.history = list()

    # def decide_tranmission(self):
    #     return
