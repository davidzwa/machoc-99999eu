import networkx as nx
import random
import math
import time

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpacerItem, QSizePolicy, QPushButton
from PyQt5.QtCore import QSize, QTimer


class Node:
    def __init__(self, key, x, y):
        self.key = key
        self.x = x
        self.y = y
        self.table = []


class RoutingEntry:
    def __init__(self, destination, next_hop, metric):
        self.destination = destination
        self.next_hop = next_hop
        self.metric = metric


class GraphGenerator(FigureCanvas):
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        self.graph = nx.Graph()
        self.window_width = 300
        self.window_height = 300
        self.node_count = 30
        self.max_edge_distance = 50
        self.max_x_displacement = 25
        self.max_y_displacement = 25

        self.nodes = {}
        self.edges = []
        self.edge_distances = []

        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def calculate_distance(self, x1, y1, x2, y2):
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance

    def get_nodes(self, node_count, min_x, max_x, min_y, max_y):
        nodes = []
        for i in range(node_count):
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            new_node = Node(i, x, y)
            nodes.append(new_node)
        return nodes

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
                    if distance < max_edge_distance and (j, i) not in edges:
                        edges.append((i, j))
                        edge_distances.append(distance)
        return edges, edge_distances

    def get_nodes_step(self, nodes, max_x_displacement, max_y_displacement):
        for i in range(len(nodes)):
            x = nodes[i].x
            y = nodes[i].y
            x += random.randint(-max_x_displacement, max_x_displacement)
            y += random.randint(-max_y_displacement, max_y_displacement)
            nodes[i].x = x
            nodes[i].y = y
        return nodes

    def set_node_count(self, count):
        self.node_count = count

    def get_node_keys(self):
        result = []
        for node in self.nodes:
            result.append(node.key)
        return result

    def create_nodes(self):
        self.nodes = self.get_nodes(
            self.node_count, 1, self.window_width, 1, self.window_height)

    def draw_next(self):
        self.get_next_step()

    def get_next_step(self):
        self.graph.clear()
        self.axes.cla()
        plt.clf()

        # Add nodes and edges
        self.nodes = self.get_nodes_step(
            self.nodes, self.max_x_displacement, self.max_y_displacement)
        self.edges, self.edge_distances = self.get_edges(
            self.nodes, self.max_edge_distance)

        node_keys = self.get_node_keys()
        self.graph.add_nodes_from(node_keys)
        for i in range(len(self.nodes)):
            self.graph.nodes[i]['pos'] = (self.nodes[i].x, self.nodes[i].y)

        self.graph.add_edges_from(self.edges)

        labels = {}
        for key in node_keys:
            labels[key] = key


        # Draw graph
        pos = nx.get_node_attributes(self.graph, 'pos')
        nx.draw(self.graph, pos, labels=labels, ax=self.axes)
        self.draw()
