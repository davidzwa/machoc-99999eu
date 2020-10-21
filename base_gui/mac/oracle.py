from typing import List

import numpy as np

from base_gui.mac.actor import Actor


class Oracle(object):
    def __init__(self, num_nodes: int, positional_spread: float):
        self.node_positions_np = None
        self.actors: List[Actor] = list()
        self.current_time = 0
        self.num_nodes = num_nodes
        self.positional_spread = positional_spread

        self.timenode_istransmitting_poisson: np.ndarray  # dtype=ActorState

    @staticmethod
    def __generate_positions(num_nodes: int, cov_diag: float):
        mean = [0, 0]
        cov = [[cov_diag, 0], [0, cov_diag]]  # Spherical distribution
        return np.random.multivariate_normal(mean, cov, num_nodes)

    @staticmethod
    def __calc_actor_distances(actor1: Actor, actor2: Actor):
        return np.linalg.norm(actor1.position - actor2.position)

    def preprocess(self,
                   time_steps: int,
                   delta_time: int,
                   transmission_chance: float,
                   transmission_range: float, packet_length: int,
                   regenerate: bool = True):
        self.transmission_chance = transmission_chance
        self.actor_range = transmission_range
        # Create empty actors
        # - name & default state
        # - provide transmission rate 'lambda'
        # Init nodes
        # - assign valid/separated 2D position
        assert len(self.actors) != 0 or regenerate is True
        if regenerate is True:
            self.node_positions_np = self.__generate_positions(self.num_nodes, self.positional_spread)
            for i, position in enumerate(self.node_positions_np):
                identifier = "N{}".format(i)
                self.actors.append(Actor(identifier, position))
            # - random positions

        # - calculate neighbours to nodes based on transmission range cutoff
        # - set IDLE state to each node
        for i, actor in enumerate(self.actors):
            copy_actors = [x for i2, x in enumerate(self.actors) if i != i2]
            for neighbour_actor in copy_actors:
                dist = self.__calc_actor_distances(actor, neighbour_actor)
                if dist < transmission_range:
                    actor.add_neighbour(neighbour_actor.state)
                    neighbour_actor.add_neighbour(actor.state)
            actor.clear_state()

        # Init sim
        # - Calculate time division: number of time-sliced atomic events
        # - Generate random 2D matrix with random binary choice
        self.delta_time = delta_time
        self.time_steps = time_steps
        self.timenode_istransmitting_random = np.random.choice(
            [0, 1],
            (self.time_steps, self.num_nodes),
            p=[1 - self.transmission_chance, self.transmission_chance])

        # Simulate each timestep
        # - Increment time (by delta)
        for time_index in range(0, self.time_steps):
            # 1) Generate new clock value and find the precalculated random transmitting actors
            transmitting_actor_indices = np.where(self.timenode_istransmitting_random[time_index] == 1)
            # 2) Update nodes with outstanding 'tranmission'
            for transmitting_actor_index in transmitting_actor_indices[0]:
                self.actors[transmitting_actor_index].attempt_transmission(
                    max_transmission_range=transmission_range,
                    packet_length=packet_length
                )
            # 3) Transform state, flatten list and store list of state of nodes in 2D time-node state matrix
            for actor in self.actors:
                actor.progress_time(self.delta_time)
            # - Update any nodes with outstanding 'arrivals' or their own 'dead messages'
            # for i, actor in enumerate(self.actors):
            #     actor.
        pass
        # Store (optional)
        # - store as JSON with parameters

    def replay(self):
        pass
        # Loop over time
        #       1) Feed state to node
        #       2) Retrieve message & distance with color/label in transit, if any (euclidian distance)


if __name__ == '__main__':
    oracle = Oracle(num_nodes=20, positional_spread=100.0)
    oracle.preprocess(time_steps=500, delta_time=1,
                      packet_length=5, transmission_range=80,
                      transmission_chance=0.15)
