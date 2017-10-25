import sys, csv
from numpy import arange, sin, pi
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, \
    QSizePolicy, QMessageBox, QLabel, QWidget, QPushButton
from PyQt5.QtCore import *
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

class App(QMainWindow):
    def __init__(self, durations, names):
        QMainWindow.__init__(self)
        self.durations = durations
        self.names = names
        self.title = 'FPT clock'
        self.state = 0

        self.setWindowTitle(self.title)

        self.label = QLabel(self.names[self.state])
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setAlignment(Qt.AlignCenter)

        self.initClock()

        self.vLayout = QVBoxLayout(self.m)  # TODO: fix windows size
        self.vLayout.addWidget(self.label)  # TODO: fix positionning

        self.show()

    def initClock(self):
        # The period is in milliseconds and we have 1000 points to plot.
        # TODO: get more accurate time measuring
        self.m = PlotCanvas(self, width=5, height=4,
                            period=self.durations[self.state]*1000/1000)
        self.m.move(0, 0)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_N and self.state < len(self.names) - 1:
            print('Stepping to next round state')
            self.state += 1

            # Delete the canvas and create a new one
            self.vLayout.removeWidget(self.m)
            self.m = None
            self.initClock()
            self.vLayout.addWidget(self.m)

            # Change the label for the state name
            self.label.setText(self.names[self.state])

            self.update()
        elif self.state >= len(self.names) - 1:
            self.close()

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

        self.plot()
        self.animate()

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
    states_durations = []
    states_names = []
    with open('states.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            states_names.append(row[0])
            states_durations.append(int(row[1]))

    app = QApplication(sys.argv)
    ex = App(states_durations, states_names)
    sys.exit(app.exec_())
