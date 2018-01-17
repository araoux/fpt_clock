import sys
import csv
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
import time, datetime


class App(QWidget):
    def __init__(self, states):
        super().__init__()
        self.title = 'FPT clock'
        self.state = 0
        self.states = states

        self.setWindowTitle(self.title)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(255,255,255))
        self.setPalette(p)

        self.label = QLabel(self.states[self.state]['name'])
        self.label.setAlignment(Qt.AlignCenter)

        # Initialize the clock
        self.m = AnalogClock(self.states[self.state]['duration'], parent=self)
        self.m.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.m.show()

        self.countDown = QLabel()

        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.label)
        self.vLayout.addWidget(self.m)
        self.vLayout.addWidget(self.countDown)
        self.setLayout(self.vLayout)

        self.childWindow = ClockControls(self)  # Clock controls
        self.childWindow.generateList(states)

        # Start at first event
        self.setEvent(0)

    def setEvent(self, i):
        if i <= len(self.states) - 1:
            self.state = i
            print('Stepping to state {}'.format(
                self.states[self.state]['name']))

            self.m.reset(self.states[self.state]['duration'])

            # Change the label for the state name
            self.label.setText(self.states[self.state]['name'])

            # Update the list
            self.childWindow.list.setCurrentItem(
                self.childWindow.statesList[self.state])

            self.update()
        else:
            self.close()

    def stepEvent(self):
        i = self.state
        self.setEvent(i+1)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_N:
            self.setEvent(self.state + 1)


class AnalogClock(QWidget):

    def __init__(self, duration, parent=None):
        super().__init__(parent)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(10)
        self.startPause = datetime.datetime.now()

        self.elapsedTimeClock = datetime.timedelta()
        self.datestart = datetime.datetime.now()

        self.duration = duration
        self.paused = True
        self.overtime = False

        self.parent = parent

        self.setMinimumSize(500, 500)

    def paintEvent(self, event):
        side = int(min(self.width(), self.height()) * 0.9 / 2)
        if not(self.paused):
            self.elapsedTimeClock = (datetime.datetime.now() - self.datestart)
        self.elapsedTime = self.elapsedTimeClock.total_seconds()

        # Create and start a QPainter
        self.painter = QPainter()

        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.Antialiasing)

        # Put the origin at the center
        self.painter.translate(self.width() / 2, self.height() / 2)

        # Setup pen and brush
        self.painter.setPen(Qt.NoPen)
        self.painter.setBrush(QColor(0, 200, 0))

        # Do the actual painting
        self.painter.save()
        currentAngle = - 2 * math.pi * self.elapsedTime / self.duration
        if not(abs(currentAngle) > 2 * math.pi):
            self.painter.drawPie(-side, -side, 2 * side, 2 * side, 90 * 16,
                                 currentAngle * (360 / (2 * math.pi)) * 16)
            self.parent.countDown.setText(
                'Time remaining : ' + str(datetime.timedelta(seconds=self.duration) - self.elapsedTimeClock))
        elif 4 * math.pi > abs(currentAngle) > 2 * math.pi:
            self.overtime = True
            self.painter.drawPie(-side, -side, 2 * side,
                                 2 * side, 90 * 16, 360 * 16)
            self.painter.setBrush(QColor(200, 0, 0))
            self.painter.drawPie(-side, -side, 2 * side, 2 * side, 90 * 16,
                                 (currentAngle + 2 * math.pi) *
                                 (360 / (2 * math.pi)) * 16)
        else:
            self.painter.setBrush(QColor(200, 0, 0))
            self.painter.drawPie(-side, -side, 2 * side,
                                 2 * side, 90 * 16, 360 * 16)
        self.painter.setPen(QColor(0, 0, 0))
        self.painter.setBrush(Qt.NoBrush)
        self.painter.drawLine(QPoint(0, 0), QPoint(
            -side * math.cos(math.pi / 2 - currentAngle),
            -side * math.sin(math.pi / 2 - currentAngle)))
        self.painter.drawArc(-side, -side, 2 * side,
                             2 * side, 90 * 16, 360 * 16)
        self.painter.restore()

        self.painter.end()

    def switchPause(self):
        if self.paused:
            self.paused = False
            # Act as if there was no pause
            self.datestart += (datetime.datetime.now() - self.startPause)
        else:
            self.paused = True
            self.startPause = datetime.datetime.now()

    def reset(self, duration):
        self.overtime = False
        self.duration = duration
        self.datestart = datetime.datetime.now()

        if self.paused:
            self.startPause = datetime.datetime.now()

        self.elapsedTimeClock = datetime.timedelta()
        self.datestart = datetime.datetime.now()


class ClockControls(QDialog):
    def __init__(self, parent,):
        QDialog.__init__(self, parent)
        self.title = 'FPT clock controls'
        self.state = 0
        self.setWindowTitle(self.title)
        self.parent = parent

        self.list = QListWidget()
        self.nextButton = QPushButton()
        self.nextButton.setText('Next')
        self.pauseButton = QPushButton()
        self.pauseButton.setText('Start')
        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.list)
        self.vLayout.addWidget(self.nextButton)
        self.vLayout.addWidget(self.pauseButton)
        self.setLayout(self.vLayout)

        self.list.currentItemChanged.connect(self.changeState)
        self.pauseButton.clicked.connect(self.switchPause)
        self.nextButton.clicked.connect(self.parent.stepEvent)

    def generateList(self, states):
        self.statesList = []
        for state in states:
            item = QListWidgetItem('{} (duration : {} s)'.format(
                state['name'], state['duration']))
            self.statesList.append(item)
            self.list.addItem(item)

    def switchPause(self):
        if self.parent.m.paused:
            self.pauseButton.setText('Pause again')
        else:
            self.pauseButton.setText('Start again')
        self.parent.m.switchPause()

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
