import sys, csv
from numpy import arange, sin, pi
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

class App(QWidget):
    def __init__(self, states):
        QMainWindow.__init__(self)
        self.title = 'FPT clock'
        self.state = 0
        self.states = states

        self.setWindowTitle(self.title)

        self.label = QLabel(self.states[self.state]['name'])
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setAlignment(Qt.AlignCenter)

        # Initialize the clock
        self.m = PlotCanvas(self, width=5, height=4, period=self.states[self.state]['duration']*1000/1000)

        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.label)
        self.vLayout.addWidget(self.m)
        self.setLayout(self.vLayout)

        self.childWindow = ClockControls(self)  # Clock controls
        self.childWindow.generateList(states)

        # Start at first event
        self.setEvent(0)

        self.childWindow.show()
        self.show()

    def setEvent(self, i):
        if i <= len(self.states) - 1:
            self.state = i
            print('Stepping to state {}'.format(self.states[self.state]['name']))

            # Delete the canvas and create a new one
            self.vLayout.removeWidget(self.m)
            self.m.close()
            del(self.m)
            self.m = PlotCanvas(self, width=5, height=4, period=self.states[self.state]['duration']*1000/1000)
            self.vLayout.addWidget(self.m)

            # Start the animation
            self.m.plot()
            self.m.animate()

            # Change the label for the state name
            self.label.setText(self.states[self.state]['name'])

            # Update the list
            self.childWindow.list.setCurrentItem(self.childWindow.statesList[self.state])

            self.update()
        else:
            self.close()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_N:
            self.setEvent(self.state + 1)

class ClockControls(QDialog):
    def __init__(self,parent,):
        QMainWindow.__init__(self,parent)
        self.title = 'FPT clock controls'
        self.state = 0
        self.setWindowTitle(self.title)
        self.parent = parent

        self.list = QListWidget()
        self.vLayout=QVBoxLayout()
        self.vLayout.addWidget(self.list)
        self.setLayout(self.vLayout)

        self.list.currentItemChanged.connect(self.changeState)

    def generateList(self, states):
        self.statesList = []
        for state in states:
            item = QListWidgetItem('{} (duration : {} s)'.format(state['name'], state['duration']))
            self.statesList.append(item)
            self.list.addItem(item)

    def changeState(self, curr):
        new_state = self.statesList.index(curr)
        self.parent.setEvent(new_state)

class PlotCanvas(FigureCanvasQTAgg):
    thetas = np.linspace(pi / 2, pi / 2 - 2 * pi, 1000, endpoint=False)

    def __init__(self, parent=None, width=5, height=4, period=20, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

        self.count_loops = 0
        self.period = period

    def __del__(self):
        self.fig.clear()
        plt.close(self.fig)

    def plot(self):
        self.ax = self.fig.add_subplot(111, polar=True)

        self.ax.grid(False)
        self.ax.set_rticks([])
        self.ax.set_xticks([])
        self.line, = self.ax.plot([pi / 2, pi / 2], [0, 1], color='black')
        self.ax.fill_between(np.array([pi / 2]), np.array([1]), color='green')

    def animate(self):
        self.anim = animation.FuncAnimation(self.fig, self.animate_loop,
                                            self.thetas, interval=self.period)
        self.draw()

    def animate_loop(self, th):
        if th == self.thetas[1]:
            self.count_loops += 1
        self.line.set_data([th, th], [0, 1])  # update the data
        ths = np.arange(pi / 2, th, -0.01)  # plot the current state
        rs = np.array(ths.shape[0] * [1])

        # Fill the clock
        for coll in (self.ax.collections):
            self.ax.collections.remove(coll)
        if self.count_loops == 2:
            self.ax.fill_between(self.thetas, np.array(self.thetas.shape[0] * [1]),
                                 color='green')
        elif self.count_loops > 2:
            self.ax.fill_between(self.thetas, np.array(self.thetas.shape[0] * [1]),
                                 color='red')
        self.ax.fill_between(ths, rs,
                             color='green' if self.count_loops <= 1 else 'red')

if __name__ == '__main__':
    states = []
    with open('states.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            states.append({'name': row[0], 'duration': int(row[1])})

    app = QApplication(sys.argv)
    ex = App(states)
    sys.exit(app.exec_())
