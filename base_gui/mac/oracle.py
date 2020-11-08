import statistics
from typing import List

import numpy as np

from base_gui.mac.actorstate import FrozenActorState
from base_gui.mac.actorstatehistory import ActorStateHistory


class Oracle(object):
    def __init__(self, num_nodes: int, positional_spread: float):
        self.node_positions_np = None
        self.actors: List[ActorStateHistory] = list()
        self.current_time = 0
        self.num_nodes = num_nodes
        self.positional_spread = positional_spread

        self.timenode_istransmitting_poisson: np.ndarray  # dtype=ActorState
        self.sim_history: np.ndarray

    @staticmethod
    def __generate_positions(num_nodes: int, cov_diag: float):
        mean = [0, 0]
        cov = [[cov_diag, 0], [0, cov_diag]]  # Spherical distribution
        return np.random.multivariate_normal(mean, cov, num_nodes, check_valid='raise')

    @staticmethod
    def __calc_actor_distances(actor1: ActorStateHistory, actor2: ActorStateHistory):
        return np.linalg.norm(actor1.position - actor2.position)

    def generate_actors(self):
        self.actors = list()
        self.node_positions_np = self.__generate_positions(self.num_nodes, self.positional_spread)
        for i, position in enumerate(self.node_positions_np):
            identifier = "N{}".format(i)
            self.actors.append(ActorStateHistory(identifier, position))

    def preprocess(self,
                   time_steps: int,
                   delta_time: int,
                   transmission_chance: float,
                   transmission_range: float, packet_length: int,
                   regenerate_positions: bool = False):
        self.transmission_chance = transmission_chance
        self.actor_range = transmission_range
        # Create empty actors
        # - name & default state
        # - provide transmission rate 'lambda'
        # Init nodes
        # - assign valid/separated random 2D position
        assert len(self.actors) != 0 or regenerate_positions is True
        if regenerate_positions is True:
            print("Pre-processing guiSimMac - generating simulation actors")
            self.generate_actors()

        # - calculate neighbours to nodes based on transmission range cutoff
        # - set IDLE state to each node
        print("Pre-processing guiSimMac - determining node neighbours")
        for i, actor in enumerate(self.actors):
            copy_actors = [x for i2, x in enumerate(self.actors) if i != i2]
            for neighbour_actor in copy_actors:
                dist = self.__calc_actor_distances(actor, neighbour_actor)
                if dist < transmission_range:
                    actor.add_neighbour(neighbour_actor.state)
                    neighbour_actor.add_neighbour(actor.state)

        print("Pre-processing guiSimMac - performing node neighbour sanity checks")
        check_actor = self.actors[0]
        for neighbour_actor_state in check_actor.state.neighbour_states:
            state_found = False
            for neighbour in self.actors:
                if neighbour_actor_state is neighbour.state:
                    state_found = True
            if state_found is False:
                raise Exception("Neighbour {} state in actor's list of neighbours was dereferenced.".format(
                    neighbour_actor_state.identifier))

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
        print("Processing guiSimMac - time steps")
        for time_index in range(0, self.time_steps):
            if (time_index % 100) == 0:
                print("Ran time index {} out of {} time steps".format(time_index, self.time_steps))
            # print("time {}".format(self.delta_time * time_index))
            # 1) propagate waves
            for actor in self.actors:
                actor.prop_messages()

            # 2) Transform state, flatten list and store list of state of nodes in 2D time-node state matrix
            # - Update any nodes with outstanding 'arrivals', MAC update and/or 'out-of-range messages'
            for actor_index, actor in enumerate(self.actors):
                actor.progress_time(self.timenode_istransmitting_random[time_index][actor_index])
            # 3) Save state
            for actor in self.actors:
                actor.save_state_to_history()
        # Flatten result
        self.sim_history = np.empty((self.time_steps, self.num_nodes), dtype=FrozenActorState)
        for index, actor in enumerate(self.actors):
            for time_index, time_actorstate in enumerate(actor.history):
                self.sim_history[time_index][index] = time_actorstate
        print("Simulation resulted in {} states stored in 'sim_history'".format(self.sim_history.size))

        final_statistics = Statistics()
        print("simulation results:")
        for actor_index, actor in enumerate(self.actors):
            stats = self.sim_history[-1][actor_index]
            print("node: {}".format(actor_index))
            print("number of collisions: {}".format(stats.num_collisions))
            print("number of dropped messages: {}".format(stats.num_dropped_messages))
            print("number of succesfull transmissions: {}".format(stats.num_successful_transmissions))
            print("number of transmission attempts: {}".format(stats.num_transmission_attempts))
            print("transmission times: {}".format(stats.transmission_times))

            final_statistics.transmission_times.extend(stats.transmission_times)
            final_statistics.num_collisions += stats.num_collisions
            final_statistics.num_dropped_messages += stats.num_dropped_messages
            final_statistics.num_successful_transmissions += stats.num_successful_transmissions
            final_statistics.num_transmission_attempts += stats.num_transmission_attempts

        final_statistics.transmission_time_stats()
        print("final counts")
        print("number of collisions: {}".format(final_statistics.num_collisions))
        print("number of dropped messages: {}".format(final_statistics.num_dropped_messages))
        print("number of succesfull transmissions: {}".format(final_statistics.num_successful_transmissions))
        print("number of transmission attempts: {}".format(final_statistics.num_transmission_attempts))

        print("transmission time statistics")
        print("min: {}\nmax: {}\nmean: {}".format(final_statistics.transmission_times_min,
                                                  final_statistics.transmission_times_max,
                                                  final_statistics.transmission_times_mean))
        print("times: {}".format(final_statistics.transmission_times))

        pass

        # Store (optional)
        # - store as JSON with parameters

    def replay(self):
        pass
        # Loop over time
        #       1) Feed state to node
        #       2) Retrieve message & distance with color/label in transit, if any (euclidian distance)


if __name__ == '__main__':
    oracle = Oracle(num_nodes=5, positional_spread=5000.0)
    oracle.generate_actors()
    oracle.preprocess(time_steps=500, delta_time=1,
                      packet_length=5, transmission_range=60,
                      transmission_chance=0.15,
                      regenerate_positions=False)
    # for actor in oracle.actors:
    # for state in actor.history:
    #     print(len(state.queued_messages))
    print("Oracle done simulating.")


class Statistics:
    num_collisions: int
    num_dropped_messages: int
    num_successful_transmissions: int
    num_transmission_attempts: int

    transmission_times: list

    def __init__(self):
        self.num_collisions = 0
        self.num_dropped_messages = 0
        self.num_successful_transmissions = 0
        self.num_transmission_attempts = 0

        self.transmission_times = list()
        self.transmission_times_min = 0
        self.transmission_times_max = 0
        self.transmission_times_mean = 0

    def transmission_time_stats(self):
        self.transmission_times.sort()
        self.transmission_times_min = min(self.transmission_times)
        self.transmission_times_max = max(self.transmission_times)
        self.transmission_times_mean = statistics.mean(self.transmission_times)
