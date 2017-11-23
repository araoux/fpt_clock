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
import math
import time

class App(QWidget):
    def __init__(self, states):
        super().__init__()
        self.title = 'FPT clock'
        self.state = 0
        self.states = states

        self.setWindowTitle(self.title)

        self.label = QLabel(self.states[self.state]['name'])
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setAlignment(Qt.AlignCenter)

        # Initialize the clock
        self.m = AnalogClock(self.states[self.state]['duration'], parent=self)
        self.m.show()

        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.label)
        self.vLayout.addWidget(self.m)
        self.setLayout(self.vLayout)

        self.childWindow = ClockControls(self)  # Clock controls
        self.childWindow.generateList(states)

        # Start at first event
        self.setEvent(0)

    def setEvent(self, i):
        if i <= len(self.states) - 1:
            self.state = i
            print('Stepping to state {}'.format(self.states[self.state]['name']))

            # Delete the canvas and create a new one
            #self.vLayout.removeWidget(self.m)
            #try:
            #    self.m.anim.stop()
            #except AttributeError:
            #    # The animation has not been defined yet
            #    print('Cannont stop an unexisting animation')
            #self.m.close()
            #del(self.m)
            #self.m = PlotCanvas(self, width=5, height=4, period=self.states[self.state]['duration']*1000/1000)
            #self.vLayout.addWidget(self.m)

            # Start the animation
            #self.m.plot()
            #self.m.animate()

            self.m.reset(self.states[self.state]['duration'])

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


class AnalogClock(QWidget):

    def __init__(self, duration, parent=None):
        super().__init__(parent)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

        self.elapsedTime = QElapsedTimer()
        self.elapsedTime.start()

        self.duration = duration

        self.overtime = False

        self.setMinimumSize(500,500)

    def paintEvent(self, event):
        side = min(self.width(), self.height())

        # Create and start a QPainter
        self.painter = QPainter()

        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.Antialiasing)

        self.painter.translate(self.width() / 2, self.height() / 2)  # Put the origin at the center

        # Setup pen and brush
        self.painter.setPen(Qt.NoPen)
        self.painter.setBrush(QColor(0, 200, 0))

        # Do the actual painting
        self.painter.save()
        currentAngle = - 2*math.pi*(self.elapsedTime.elapsed()/1000)/self.duration
        if not(abs(currentAngle) > 2*math.pi):
            self.painter.drawPie(-200, -200, 400, 400, 90*16, currentAngle*(360/(2*math.pi))*16)
        elif 4*math.pi > abs(currentAngle) > 2*math.pi:
            self.overtime = True
            self.painter.drawPie(-200, -200, 400, 400, 90*16, 360*16)
            self.painter.setBrush(QColor(200, 0, 0))
            self.painter.drawPie(-200, -200, 400, 400, 90*16, (currentAngle + 2*math.pi)*(360/(2*math.pi))*16)
        else:
            self.painter.setBrush(QColor(200, 0, 0))
            self.painter.drawPie(-200, -200, 400, 400, 90*16, 360*16)
        self.painter.restore()

        self.painter.end()

    def reset(self, duration):
        self.overtime = False
        self.duration = duration
        self.elapsedTime.restart()


class ClockControls(QDialog):
    def __init__(self,parent,):
        QDialog.__init__(self,parent)
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


if __name__ == '__main__':
    states = []
    with open('states.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            states.append({'name': row[0], 'duration': int(row[1])})

    app = QApplication(sys.argv)
    ex = App(states)
    ex.show()
    ex.childWindow.show()
    sys.exit(app.exec_())
