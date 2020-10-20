import numpy as np
import pygame
from pygame import Vector2

from base_gui.app_logging import LOGGER
from base_gui.gui_components.game import Game
from base_gui.simulation.node import Node


class GuiSim(Game):
    node_positions: np.ndarray
    data_nodes: list

    def __init__(self, game_size: Vector2, sim_rect, local_origin):
        super(GuiSim, self).__init__(game_size)

        self.sim_rect = sim_rect
        self.local_origin = local_origin

    def generate_nodes_multivariate(self, num_nodes: int, cov_diag=1):
        """
        Generate data nodes in a multivariate normal distribution. The covariance diagonal determines
        whether they distribute spherical (x=y) or diagonally. We always prefer
        """
        mean = [0, 0]
        cov = [[cov_diag, 0], [0, cov_diag]]  # Spherical distribution
        node_positions_np = np.random.multivariate_normal(mean, cov, num_nodes)
        self.generate_nodes(node_positions_np)
        LOGGER.info("Generated {} multivariate nodes 2D".format(num_nodes))

    def generate_nodes(self, node_positions_np):
        """
        Generate data nodes as specified by the input data array.
        """
        self.node_positions = node_positions_np
        self.data_nodes = list()
        indexer = 0
        for node_pos in node_positions_np:
            indexer+=1
            dot_node = Node(position_meters=Vector2(tuple(node_pos)),
                            reference_frame=self.sim_rect,
                            screen=self.screen,
                            local_origin=self.local_origin,
                            color=pygame.Color("red"),
                            node_title="N{}".format(indexer))
            self.data_nodes.append((dot_node))

    def render_datanodes(self, disable_node_titles = False):
        for sim_node in self.data_nodes:
            sim_node.render(disable_node_titles)
