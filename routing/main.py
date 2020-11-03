from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QTableWidgetSelectionRange, QWidget, QMainWindow, QAction, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpacerItem, QSizePolicy, QPushButton, QSlider
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import math

import sys
import random
import time
import threading
import asyncio

from networkx.classes import graph
from graph_generator import GraphGenerator

class WinTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = "Table for node {}".format(0)
        self.top    = 50
        self.left   = 1450
        self.width  = 450
        self.height = 960
        self.index = 0
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.createTable()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout)
        try:
            index = [i for i,__ in enumerate(mainWin.graph.n.nodes) if mainWin.graph.n.nodes[i].key == self.index][0]
        except:
            index = 0
        self.setWindowTitle("Table for node {}".format(index))
        self.show()

    def createTable(self):
       # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(mainWin.graph.n.nodes))
        self.tableWidget.setColumnCount(4)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(['Destination', 'Next hop', 'Metric', 'Sequence number'])
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        try:
            index = [i for i,__ in enumerate(mainWin.graph.n.nodes) if mainWin.graph.n.nodes[i].key == self.index][0]
        except:
            index = 0
        for x, entry in enumerate(mainWin.graph.n.nodes[index].table):
            self.tableWidget.setItem(x,0, QTableWidgetItem(str(entry.destination)))
            self.tableWidget.setItem(x,1, QTableWidgetItem(str(entry.next_hop)))
            self.tableWidget.setItem(x,2, QTableWidgetItem(str(entry.metric)))
            self.tableWidget.setItem(x,3, QTableWidgetItem(str(entry.sequence_number)))
            self.tableWidget.move(0,0)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(500, 350) 

        self.title = 'Ad-hoc networks routing protocol visualisation'
        self.left = 50
        self.top = 50
        self.width = 1200
        self.height = 800
        self.graph = GraphGenerator()
        self.simulating = False
        self.timestep = 0

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.statusBar().showMessage('Ready for simulation')

        widget = QWidget(self)
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
        self.add_node_button = QPushButton('Add one node', self)
        self.add_node_button.clicked.connect(self.add_node)
        self.remove_random_button = QPushButton('Remove random node', self)
        self.remove_random_button.clicked.connect(self.remove_random_node)
        self.start_simulation_button = QPushButton('Start simulation', self)
        self.start_simulation_button.clicked.connect(self.start_simulation)
        self.stop_simulation_button = QPushButton('Stop simulation', self)
        self.stop_simulation_button.clicked.connect(self.stop_simulation)
        self.show_table_button = QPushButton('Show table for node:', self)
        self.show_table_button.clicked.connect(self.show_table)

        self.table_index = QLineEdit(self)
        self.table_index.setFixedWidth(20)
        self.table_index.setText("")

        hlay2 = QHBoxLayout()
        hlay2.addWidget(self.create_button)
        hlay2.addWidget(self.add_node_button)
        hlay2.addWidget(self.remove_random_button)
        hlay2.addItem(QSpacerItem(1000, 10, QSizePolicy.Expanding))
        hlay2.addWidget(self.start_simulation_button)
        hlay2.addWidget(self.stop_simulation_button)
        hlay2.addWidget(self.show_table_button)
        hlay2.addWidget(self.table_index)
        vlay.addLayout(hlay2)
        self.graph = GraphGenerator(self, width=5, height=4, dpi=100)
        vlay.addWidget(self.graph)
        hlay3 = QHBoxLayout()
        self.backwards_button = QPushButton('Go back in time', self)
        self.backwards_button.clicked.connect(self.backwards)
        self.forwards_button = QPushButton('Go forward in time', self)
        self.forwards_button.clicked.connect(self.forwards)


        hlay3.addWidget(self.backwards_button)
        hlay3.addItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        hlay3.addWidget(self.forwards_button)
        vlay.addLayout(hlay3)

        hlay4 = QHBoxLayout()
        self.label = QLabel()
        self.label.setText("Current step: " + str(1))
        hlay4.addItem(QSpacerItem(50, 10, QSizePolicy.Expanding))
        hlay4.addWidget(self.label)
        hlay4.addItem(QSpacerItem(50, 10, QSizePolicy.Expanding))
        vlay.addLayout(hlay4)

        self.stop_simulation_button.setEnabled(False)
        self.backwards_button.setEnabled(False)
        self.forwards_button.setEnabled(False)

        self.graph.n.create_nodes()
        self.graph.draw_next()

    def create_nodes(self):
        number_of_nodes = 10
        if self.line.text().isnumeric():
            number_of_nodes = int(self.line.text())
        self.graph.n.set_node_count(number_of_nodes)
        self.graph.n.create_nodes()
        self.graph.nodes_timesteps.clear()
        self.graph.draw_next()

    def add_node(self):
        self.graph.n.node_count += 1
        self.graph.draw_next(step=False)

    def backwards(self):
        if self.graph.current_step - 1 > abs(self.timestep):
            self.timestep -= 1
            self.graph.jump_in_time(timestep = self.timestep)
        else:
            self.backwards_button.setEnabled(False)
        if self.timestep < 0:
            self.forwards_button.setEnabled(True)
        self.label.setText("Current step: " + str(self.graph.current_step + self.timestep))
    
    def forwards(self):
        if self.timestep < 0:
            self.forwards_button.setEnabled(True)
            self.timestep += 1
            self.graph.jump_in_time(timestep = self.timestep)
        else:
            self.forwards_button.setEnabled(False)
        if self.graph.current_step - 1> abs(self.timestep):
            self.backwards_button.setEnabled(True)
        self.label.setText("Current step: " + str(self.graph.current_step + self.timestep))


    def remove_random_node(self):
        self.graph.n.node_count -= 1
        self.graph.draw_next(step=False)

    def start_simulation(self):
        def step():
            self.graph.draw_next()
            self.label.setText("Current step: " + str(self.graph.current_step + self.timestep))
            time.sleep(1)
            if self.simulating: 
                if self.timestep < 0:
                    self.forwards()
                    step()
                else:
                    step()

        self.statusBar().showMessage('Simulating...')
        self.simulating = True
        self.create_button.setEnabled(False)
        self.start_simulation_button.setEnabled(False)
        self.stop_simulation_button.setEnabled(True)
        self.backwards_button.setEnabled(True)
        self.forwards_button.setEnabled(True)

        simulation_timer = threading.Thread(target=step)
        simulation_timer.start()

    def stop_simulation(self):
        self.statusBar().showMessage('Simulation stopped.')
        self.simulating = False
        self.create_button.setEnabled(True)
        self.start_simulation_button.setEnabled(True)
        self.stop_simulation_button.setEnabled(False)

    def show_table(self):
        index = 0
        if self.table_index.text().isnumeric():
            index = int(self.table_index.text())
        self.winTable = WinTable()
        self.winTable.index = index
        self.winTable.initUI()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
