from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpacerItem, QSizePolicy, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import sys
import random
import time
import threading
import asyncio
from graph_generator import GraphGenerator

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.title = 'Ad-hoc networks routing protocol visualisation'
        self.left = 50
        self.top = 50
        self.width = 1200
        self.height = 800
        self.graph = GraphGenerator()
        self.simulating = False

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.statusBar().showMessage('Ready for simulation')

        widget =  QWidget(self)
        self.setCentralWidget(widget)
        vlay = QVBoxLayout(widget)
        hlay = QHBoxLayout()
        vlay.addLayout(hlay)

        self.nameLabel = QLabel('Number of nodes:', self)
        self.line = QLineEdit(self)
        self.line.setFixedWidth(50)
        self.line.setText("10")

        hlay.addWidget(self.nameLabel)
        hlay.addWidget(self.line)
        hlay.addItem(QSpacerItem(1000, 10, QSizePolicy.Expanding))

        self.create_button = QPushButton('Create nodes', self)
        self.create_button.clicked.connect(self.create_nodes)
        self.start_simulation_button = QPushButton('Start simulation', self)
        self.start_simulation_button.clicked.connect(self.start_simulation)
        self.stop_simulation_button = QPushButton('Stop simulation', self)
        self.stop_simulation_button.clicked.connect(self.stop_simulation)
        hlay2 = QHBoxLayout()
        hlay2.addWidget(self.create_button)
        hlay2.addWidget(self.start_simulation_button)
        hlay2.addWidget(self.stop_simulation_button)
        hlay2.addItem(QSpacerItem(1000, 10, QSizePolicy.Expanding))
        vlay.addLayout(hlay2)
        self.graph = GraphGenerator(self, width=5, height=4, dpi=100)
        vlay.addWidget(self.graph)

        self.stop_simulation_button.setEnabled(False)

        self.graph.create_nodes()
        self.graph.draw_next()

    def create_nodes(self):
        number_of_nodes = 10
        if self.line.text().isnumeric():
            number_of_nodes = int(self.line.text())
        self.graph.set_node_count(number_of_nodes)
        self.graph.create_nodes()
        self.graph.draw_next()

    def start_simulation(self):
        def step():
            self.graph.draw_next()
            time.sleep(1)
            if self.simulating:
                step()

        self.statusBar().showMessage('Simulating...')
        self.simulating = True
        self.create_button.setEnabled(False)
        self.start_simulation_button.setEnabled(False)
        self.stop_simulation_button.setEnabled(True)

        simulation_timer = threading.Thread(target=step)
        simulation_timer.start()

    def stop_simulation(self):
        self.statusBar().showMessage('Simulation stopped.')
        self.simulating = False
        self.create_button.setEnabled(True)
        self.start_simulation_button.setEnabled(True)
        self.stop_simulation_button.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
