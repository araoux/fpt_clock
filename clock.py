#---------Imports
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as Tk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#---------End of imports

fig = plt.Figure()
global filling


def animate(th):
    line.set_data([th,th],[0,1])  # update the data
    ths = np.arange(pi/2,th,-0.01)
    rs = np.array(ths.shape[0]*[1])
    for coll in (ax.collections):
        ax.collections.remove(coll)
    ax.fill_between(ths,rs,color='green')
    return line

root = Tk.Tk()

label = Tk.Label(root,text="SHM Simulation").grid(column=0, row=0)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=1)

ax = fig.add_subplot(111, polar=True)
ax.grid(False)
ax.set_rticks([])
ax.set_xticks([])
line, = ax.plot([pi/2,pi/2],[0,1],color='black')
ax.fill_between(np.array([pi/2]),np.array([1]),color='green')
ani = animation.FuncAnimation(fig, animate, np.linspace(pi/2,pi/2-2*pi,100,endpoint=False), interval=25, blit=False)

Tk.mainloop()
