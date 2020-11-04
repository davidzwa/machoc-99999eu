from typing import List

import pygame
from pygame import Vector2

from base_gui.constants import MENU_CHECKBOXES_GENERIC, MENU_CHECKBOX_NODELABELS_INDEX, \
    MENU_CHECKBOXES_MAC, SimConsts
from base_gui.gui_components.game import Game
from base_gui.mac.actorstate import FrozenActorState
from base_gui.mac.oracle import Oracle
from base_gui.simulation.node import Node


class GuiSimMac(Game):
    def __init__(self, game_size: Vector2, sim_rect, local_origin):
        super(GuiSimMac, self).__init__(game_size)
        self.data_nodes: List[Node]

        self.sim_rect = sim_rect
        self.local_origin = local_origin
        self.oracle: Oracle

        self.show_oracle_states_timeindex = 0

    def generate_oracle(self, num_nodes, positional_spread):
        self.oracle = Oracle(num_nodes=num_nodes, positional_spread=positional_spread)
        self.oracle.generate_actors()
        self.generate_nodes()

    def run_oracle_preprocess(self, time_steps, time_delta):
        assert self.oracle is not None
        self.oracle.preprocess(time_steps=time_steps, delta_time=time_delta,
                               packet_length=SimConsts.PACKET_LENGTH_SPACE,
                               transmission_range=SimConsts.TRANSMISSION_RANGE,
                               transmission_chance=SimConsts.TRANSMISSION_CHANCE,
                               regenerate_positions=False)

    # def generate_nodes_multivariate(self, num_nodes: int, cov_diag=1):
    #     """
    #     Generate data nodes in a multivariate normal distribution. The covariance diagonal determines
    #     whether they distribute spherical (x=y) or diagonally. We always prefer spherical as it is most natural.
    #     """
    #     mean = [0, 0]
    #     cov = [[cov_diag, 0], [0, cov_diag]]  # Spherical distribution
    #     node_positions_np = np.random.multivariate_normal(mean, cov, num_nodes)
    #     self.generate_nodes(node_positions_np)
    #     LOGGER.info("Generated {} multivariate nodes 2D".format(num_nodes))

    def generate_nodes(self):
        """
        Generate data nodes as specified by the input data array.
        """
        assert self.oracle is not None
        self.data_nodes = list()
        indexer = 0
        for node_pos in self.oracle.node_positions_np:
            dot_node = Node(position_meters=Vector2(tuple(node_pos)),
                            reference_frame=self.sim_rect,
                            screen=self.screen,
                            local_origin=self.local_origin,
                            color=pygame.Color("red"),
                            node_title="N{}".format(indexer))
            indexer += 1
            self.data_nodes.append(dot_node)

    def add_nav_checkboxgroup_specific(self, sim_labels: tuple = MENU_CHECKBOXES_MAC):
        """
        Add two checkbox groups
        """
        # Example
        self.side_menu.clear_checkbox_groups()
        self.add_nav_checkboxgroup_generic(MENU_CHECKBOXES_GENERIC)
        self.add_nav_checkboxgroup_generic(sim_labels)

    def show_next_oracle_timeindex(self):
        if self.oracle.time_steps - 1 > self.show_oracle_states_timeindex:
            self.show_oracle_states_timeindex += 1
        else:
            self.show_oracle_states_timeindex = 0
        self.draw_oraclestate_waves(self.show_oracle_states_timeindex)

    def draw_oraclestate_waves(self, time: int):
        sim_state: List[FrozenActorState] = self.oracle.sim_history[time]

        assert sim_state is not None
        for index, state in enumerate(sim_state):
            assert state.identifier == self.data_nodes[index].node_title
            # print(index, state.identifier, self.data_nodes[index].node_title)
            intransit_message_distances = list()
            intransit_message_types = list()
            for message in state.in_transit_messages:
                intransit_message_distances.append(
                    Vector2(message.prop_distance - message.prop_packet_length, message.prop_distance)
                )
                intransit_message_types.append(message.type)

            self.data_nodes[index].set_wavefronts(intransit_message_distances, intransit_message_types)
            self.data_nodes[index].set_color_by_state(state.macState)
        pass

    def render_datanodes(self):
        node_labels_state = self.get_checkbox_value(0, MENU_CHECKBOX_NODELABELS_INDEX)
        for sim_node in self.data_nodes:
            sim_node.render(node_labels_state)
            sim_node.render_waves()
