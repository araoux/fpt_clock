#---------Imports
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as Tk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
#---------End of imports

# Define the different states of the clock
states = [10, 60, 120]
states_values = ['initial', 'during', 'final']

global fig
fig = plt.Figure()
global state, states_value
state = states.pop(0)
state_value = states_values.pop(0)
global count_loops
count_loops = 0
global ani


def animate(th):
    global count_loops
    if th == thetas[1]:
        count_loops += 1
    # print(count_loops)
    line.set_data([th, th], [0, 1])  # update the data
    ths = np.arange(pi / 2, th, -0.01)  # plot the current state of the clock
    rs = np.array(ths.shape[0] * [1])

    # Fill the clock
    for coll in (ax.collections):
        ax.collections.remove(coll)
    if count_loops == 2:
        ax.fill_between(thetas, np.array(thetas.shape[0] * [1]), color='green')
    elif count_loops > 2:
        ax.fill_between(thetas, np.array(thetas.shape[0] * [1]), color='red')
    ax.fill_between(ths, rs, color='green' if count_loops <= 1 else 'red')
    return line


def next_state(event):
    """This function changes the clock state to the next state defined in the
    states array"""
    global count_loops, ani
    if len(states) > 0:
        state_value = states_values.pop(0)
        print('Stepping to next state :', state_value)
        state = states.pop(0)
        count_loops = 0

        ani.frame_seq = ani.new_frame_seq()
        # TODO: make the new frame take in account the new interval between
        # frames...
    else:
        print('End of round')
        root.quit()


root = Tk.Tk()
label = Tk.Label(root, text="FPT clock").grid(column=0, row=0)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0, row=1)
canvas._tkcanvas.bind("<Left>", next_state)

ax = fig.add_subplot(111, polar=True)
ax.grid(False)
ax.set_rticks([])
ax.set_xticks([])
line, = ax.plot([pi / 2, pi / 2], [0, 1], color='black')  # Initial clock hand
ax.fill_between(np.array([pi / 2]), np.array([1]), color='green')
thetas = np.linspace(
    pi / 2, pi / 2 - 2 * pi, 1000, endpoint=False)
ani = animation.FuncAnimation(fig, animate, thetas, interval=state, blit=False)

Tk.mainloop()
