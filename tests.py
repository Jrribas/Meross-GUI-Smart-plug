import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import matplotlib.animation as animation
from matplotlib import style
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from meross_iot.api import MerossHttpClient
import datetime as dt
import numpy as np


x = np.linspace(0, 2*np.pi, 400)
y = np.sin(x**2)


#Creates just a figure and only one subplot
fig, ax = plt.subplots(1,2, figsize=(19,6))
ax[0].plot(x, y)
ax[0].set_title('Simple plot')

plt.show()

