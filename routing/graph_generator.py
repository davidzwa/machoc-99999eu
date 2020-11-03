from typing import Sequence, Tuple
import networkx as nx
import random
import math
import time
from copy import deepcopy

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpacerItem, QSizePolicy, QPushButton
from PyQt5.QtCore import QSize, QTimer

kcount = 0

class Node:
    def __init__(self, key, x, y):
        self.key = key
        self.x = x
        self.y = y
        self.table = []


class RoutingEntry:
    def __init__(self, destination, next_hop, metric, sequence_number=None):
        self.destination = destination
        self.next_hop = next_hop
        self.metric = metric
        self.sequence_number = sequence_number

class Graph:
    def __init__(self, node_count, window_height, window_width, edge_distance):
        self.nodes = []
        self.edges = []
        self.node_count = node_count
        self.window_height = window_height
        self.window_width = window_width
        self.max_edge_distance = edge_distance

    def remove_random_node(self):
        if len(self.nodes) > 0:
            node_index = random.randint(0, len(self.nodes) - 1)
            node_key = self.nodes[node_index].key
            del self.nodes[node_index]

            for i, edge in enumerate(self.edges):
                if node_key in edge:
                    del self.edges[i]

            for node in self.nodes:
                for i, entry in enumerate(node.table):
                    if entry.destination == node_key:
                        del node.table[i]
        return self.nodes

    def set_node_count(self, count):
        self.node_count = count

    def calculate_distance(self, x1, y1, x2, y2):
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance

    def update_sequence(self, sequence, fail=False):
        sequence_nr = int(sequence.split('-')[1])
        if sequence_nr % 2 == 1 and fail:
            sequence_nr += 2
        elif sequence_nr % 2 == 0 and fail:
            sequence_nr += 1
        elif sequence_nr % 2 == 1 and not fail:
            sequence_nr += 1
        else:
            sequence_nr += 2
        return sequence.split('-')[0] + '-' + str(sequence_nr).zfill(3)

    def get_sequence_number(self, sequence):
        return int(sequence.split('-')[1])

    def broadcast_table(self):
        for i in range(self.node_count - 1): #|V| - 1 is enough
            for node in self.nodes:
                for entry in node.table:
                    if entry.metric == 1:
                        index = [i for i,x in enumerate(self.nodes) if self.nodes[i].key == entry.destination][0]
                        self.share_table(node, self.nodes[index])

    def get_node_by_key(self, key):
        result = None
        for node in self.nodes:
            if node.key == key:
                result = node
        return result

    def broadcast_to_neighbours(self, node):
        for entry in node.table:
            if entry.metric == 1:
                self.share_table(node, self.get_node_by_key(entry.destination))

    def broadcast_broken_link(self, node1, node2):
        print("Broken: ", node1.key, node2.key)
        for node1_entry in node1.table:
            if node1_entry.destination == node2.key or node1_entry.next_hop == node2.key:
                node1_entry.metric = float("inf")
                node1_entry.sequence_number = self.update_sequence(node1_entry.sequence_number, True)
                node1_entry.next_hop = None

        for node2_entry in node2.table:
            if node2_entry.destination == node1.key or node2_entry.next_hop == node1.key:
                node2_entry.metric = float("inf")
                node2_entry.sequence_number = self.update_sequence(node2_entry.sequence_number, True)
                node2_entry.next_hop = None
    
        self.broadcast_to_neighbours(node1)
        self.broadcast_to_neighbours(node2)

    def broadcast_new_link(self, node1, node2):
        for node1_entry in node1.table:
            if node1_entry.destination == node2.key:
                node1_entry.metric = 1
                node1_entry.sequence_number = self.update_sequence(node1_entry.sequence_number, False)
                node1_entry.next_hop = node2.key

        for node2_entry in node2.table:
            if node2_entry.destination == node1.key:
                node2_entry.metric = 1
                node2_entry.sequence_number = self.update_sequence(node2_entry.sequence_number, False)
                node2_entry.next_hop = node1.key
    
        self.broadcast_to_neighbours(node1)
        self.broadcast_to_neighbours(node2)


    def share_table(self, node1, node2):
        broadcast = False
        for i, node2_entry in enumerate(node2.table):
            node1_entry = node1.table[i]

            node1_number = self.get_sequence_number(node1_entry.sequence_number)
            node2_number = self.get_sequence_number(node2_entry.sequence_number)
            if node1_number > node2_number:
                # New sequence, so update table in node 2
                node2_entry.metric = node1_entry.metric + 1
                if node1_entry.metric != float("inf"):
                    node2_entry.next_hop = node1.key
                else:
                    node2_entry.next_hop = None
                node2_entry.sequence_number = node1_entry.sequence_number
                broadcast = True

            if node2_entry.next_hop == node1.key:
                if node1.table[i].metric == float("inf"):
                    node2_entry.metric = float("inf")
                    node2_entry.next_hop = None
                    node2_entry.sequence_number = self.update_sequence(node2_entry.sequence_number, True)
                    broadcast = True
        
        if broadcast:
            self.broadcast_to_neighbours(node2)


    def periodic_update(self):
        for node in self.nodes:
            for entry in node.table:
                if int(entry.destination) == int(node.key):
                    entry.sequence_number = self.update_sequence(entry.sequence_number, False)
                
            self.broadcast_to_neighbours(node)

    def add_to_table(self, new_node):
        for node in self.nodes:
            if node.key != new_node.key:
                new_entry = RoutingEntry(new_node.key, None, float('inf'), str(new_node.key) + '-000')
                node.table.append(new_entry)
        for node in self.nodes:
            if node.key == new_node.key:
                new_entry = RoutingEntry(node.key, node.key, 0, str(new_node.key) + '-000')
                new_node.table.append(new_entry)                        
            else:
                new_entry = RoutingEntry(node.key, None, float('inf'), str(node.key) + '-000')
                new_node.table.append(new_entry)
        self.broadcast_to_neighbours(new_node)


    def fill_table(self):
        for node in self.nodes:
            for i in range(len(self.nodes)):
                if self.nodes[i].key != node.key:
                    node.table.append(RoutingEntry(self.nodes[i].key, None, float('inf'), str(self.nodes[i].key) + '-000'))
                else:
                    node.table.append(RoutingEntry(node.key, node.key, 0, str(node.key) + '-002'))
        for node in self.nodes:
            for edge in self.edges:
                if node.key == edge[0]:
                    node.table[self.nodes[edge[1]].key].metric = 1
                    node.table[self.nodes[edge[1]].key].next_hop = self.nodes[edge[1]].key
                    self.nodes[edge[1]].table[node.key].metric = 1
                    self.nodes[edge[1]].table[node.key].next_hop = node.key

        for node in self.nodes:
            self.broadcast_to_neighbours(node)

    def add_one_node(self):
        self.nodes.append(self.get_new_node(
            1, self.window_width, 1, self.window_height))

    def get_new_node(self, min_x, max_x, min_y, max_y):
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)

        new_node_key = 0
        if len(self.nodes) > 0:
            new_node_key = self.nodes[len(self.nodes) - 1].key + 1
        return Node(new_node_key, x, y)

    def get_edges(self, nodes, max_edge_distance):
        edges = []
        edge_distances = []
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j:
                    node1 = nodes[i]
                    node2 = nodes[j]
                    distance = self.calculate_distance(
                        node1.x, node1.y, node2.x, node2.y)
                    if distance < max_edge_distance and (node2.key, node1.key) not in edges:
                        edges.append((node1.key, node2.key))
                        edge_distances.append(distance)
        return edges, edge_distances

    def get_nodes(self, node_count, min_x, max_x, min_y, max_y):
        nodes = []
        for i in range(node_count):
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            new_node = Node(i, x, y)
            nodes.append(new_node)
        return nodes

    def create_nodes(self):
        self.nodes = self.get_nodes(
            self.node_count, 1, self.window_width, 1, self.window_height)
        self.edges, self.edge_distances = self.get_edges(
            self.nodes, self.max_edge_distance)
        #self.fill_table()

class GraphGenerator(FigureCanvas):
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        self.graph = nx.Graph()
        self.max_x_displacement = 10
        self.max_y_displacement = 10
        self.node_count = 20
        self.window_width = 300
        self.window_height = 300
        self.max_edge_distance = 50

        self.n = Graph(self.node_count, self.window_height, self.window_width, self.max_edge_distance)

        self.current_step = 0
        self.nodes_timesteps = []

        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def get_nodes_step(self, nodes, max_x_displacement, max_y_displacement):
        for i in range(len(nodes)):
            x = nodes[i].x
            y = nodes[i].y
            x += random.randint(-max_x_displacement, max_x_displacement)
            y += random.randint(-max_y_displacement, max_y_displacement)
            nodes[i].x = x
            nodes[i].y = y
        self.nodes_timesteps.append(deepcopy(nodes))
        return nodes

    def get_node_keys(self):
        result = []
        for node in self.n.nodes:
            result.append(node.key)
        return result

    def draw_next(self, step=True):
        self.get_next_step(step)

    def check_edges(self, timestep):
        if len(self.nodes_timesteps) > 1:
            previous_nodes = self.nodes_timesteps[timestep - 2]
            previous_edges, __ = self.n.get_edges(previous_nodes, self.n.max_edge_distance)
            removed_edges =  set(previous_edges) - set(self.n.edges)
            new_edges =  set(self.n.edges) - set(previous_edges)

            for edge in removed_edges:
                self.n.broadcast_broken_link(self.n.get_node_by_key(edge[0]), self.n.get_node_by_key(edge[1]))
            for edge in new_edges:
                self.n.broadcast_new_link(self.n.get_node_by_key(edge[0]), self.n.get_node_by_key(edge[1]))
        
    def jump_in_time(self, timestep=0):
        self.get_next_step(step=False, timestep=timestep)

    def get_next_step(self, step=True, timestep=0):
        self.graph.clear()
        self.axes.cla()
        plt.clf()

        # Add nodes and edges
        if step:
            self.n.nodes = self.get_nodes_step(
                self.n.nodes, self.max_x_displacement, self.max_y_displacement)
        elif self.n.node_count > len(self.n.nodes):
            self.n.add_one_node()
            self.n.add_to_table(self.n.nodes[-1])
            self.nodes_timesteps.append(deepcopy(self.n.nodes))
        elif self.n.node_count < len(self.n.nodes):
            self.nodes_timesteps.append(deepcopy(self.n.remove_random_node()))
        try:
            self.n.nodes = deepcopy(self.nodes_timesteps[timestep-1])
        except:
            pass
        self.n.edges, self.n.edge_distances = self.n.get_edges(
            self.n.nodes, self.n.max_edge_distance)
        if(len(self.nodes_timesteps) == 1):
            self.n.fill_table()

        node_keys = self.get_node_keys()
        self.graph.add_nodes_from(node_keys)
        for i, node in enumerate(self.n.nodes):
            self.graph.nodes[node.key]['pos'] = (
                self.n.nodes[i].x, self.n.nodes[i].y)


        self.graph.add_edges_from(self.n.edges)

        self.n.periodic_update()
        self.check_edges(timestep)
        self.n.periodic_update()

        labels = {}
        for key in node_keys:
            labels[key] = key

        # Draw graph
        pos = nx.get_node_attributes(self.graph, 'pos')
        nx.draw(self.graph, pos, labels=labels, ax=self.axes)
        self.draw()
        if timestep == 0:
            self.current_step += 1
