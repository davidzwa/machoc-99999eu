import uuid
from typing import List

import numpy as np

from base_gui.mac.actorstate import ActorState, FrozenActorState
from base_gui.mac.message import Message, MessageType, MESSAGE_DISTANCE_PER_TIME


class ActorStateHistory(object):
    def __init__(
            self,
            identifier: str,
            position: np.ndarray,
            state=None):

        self.identifier = identifier
        self.position: np.ndarray = position

        if state is None:
            self.state: ActorState = ActorState(identifier, 0.0, self.position)
        else:
            self.state = state
        self.history: List[FrozenActorState] = list()

    def add_neighbour(self, neighbour_state: ActorState):
        self.state.add_neighbour_state(neighbour_state)
        pass

    def save_state_to_history(self):
        frozen_state: FrozenActorState = self.state.get_frozen_state()
        self.history.append(frozen_state)

    def progress_time(self, new_message):
        self.state.progress_actorstate_time(new_message)
