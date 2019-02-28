import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from meross_iot.api import MerossHttpClient
import datetime as dt

################################################

E = tk.E
W = tk.W
N = tk.N
S = tk.S

################################################

matplotlib.use("TkAgg")
LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)


################################################

date = [dt.datetime.now()]
power = [0]
currentA = [0]
currentmA = [0]
voltage = [0]
device1 = None
c = 0

plt.style.use('ggplot')
fig, ax = plt.subplots(3, 1, sharex="all")


################################################


def toggle_password(c1, e2):

    if c1.var.get():
        e2['show'] = "*"
    else:
        e2['show'] = ""


def popupmsg(msg):

    popup = tk.Tk()

    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.grid(row=1, column=1, padx=2, pady=2)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy())
    B1.grid(row=2, column=1, padx=2, pady=2)

    popup.grid_rowconfigure(0, weight=1)
    popup.grid_rowconfigure(3, weight=1)
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_columnconfigure(2, weight=1)

    popup.mainloop()


def animate(i):

    global c, device1

    electricity = device1.get_electricity()

    if c == 0:
        power[0] = electricity["electricity"]["power"] / 1000
        voltage[0] = electricity["electricity"]["voltage"] / 10
        currentmA[0] = electricity["electricity"]["current"] / 10
        currentA[0] = electricity["electricity"]["current"] / 10000
        date[0] = dt.datetime.now()
        c = c + 1

    else:
        power.append(electricity["electricity"]["power"] / 1000)
        voltage.append(electricity["electricity"]["voltage"] / 10)
        currentmA.append(electricity["electricity"]["current"]/10)
        currentA.append(electricity["electricity"]["current"]/10000)
        date.append(dt.datetime.now())

    plt.cla()

    ax[0].plot(date, power, 'r-o')
    ax[1].plot(date, voltage, 'b-o')
    if electricity["electricity"]["current"] < 9999:
        ax[2].plot(date, currentmA, 'g-o')
    else:
        ax[2].plot(date, currentA, 'g-o')

    ax[0].set_xlabel("Time", fontweight='extra bold', fontsize='x-large')
    ax[0].set_ylabel("Power", fontweight='extra bold', fontsize='x-large')
    ax[1].set_xlabel("Time", fontweight='extra bold', fontsize='x-large')
    ax[1].set_ylabel("Voltage", fontweight='extra bold', fontsize='x-large')
    ax[2].set_xlabel("Time", fontweight='extra bold', fontsize='x-large')
    ax[2].set_ylabel("Current", fontweight='extra bold', fontsize='x-large')

    locator = mdates.AutoDateLocator()
    formatter = mdates.AutoDateFormatter(locator)

    ax[0].xaxis.set_major_locator(locator)
    ax[0].xaxis.set_major_formatter(formatter)
    ax[1].xaxis.set_major_locator(locator)
    ax[1].xaxis.set_major_formatter(formatter)
    ax[2].xaxis.set_major_locator(locator)
    ax[2].xaxis.set_major_formatter(formatter)

    fig.autofmt_xdate()
    fig.tight_layout()

################################################


class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas_, parent_):
        self.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            (None, None, None, None),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            (None, None, None, None),
            ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
            )
        NavigationToolbar2Tk.__init__(self, canvas_, parent_)


class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self._frame = None
        tk.Tk.wm_title(self, "Smart Plug Monitoring")
        # tk.Tk.iconbitmap(self, default="clienticon.ico")
        self.switch_frame(StartPage)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(tk.Frame(self))
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=lambda: popupmsg("Not supported just yet!"))
        filemenu.add_command(label="Open", command=lambda: popupmsg("Not supported just yet!"))
        filemenu.add_separator()
        filemenu.add_command(label="Export Data", command=lambda: popupmsg("Not supported just yet!"))
        menubar.add_cascade(label="File", menu=filemenu)

        tk.Tk.config(self, menu=menubar)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid(sticky=N+S+E+W)


class StartPage(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        l1 = ttk.Label(self, text="Authentication Page", font=("Verdana", 10, "bold"))
        l2 = ttk.Label(self, text="Username", font=NORM_FONT)
        l3 = ttk.Label(self, text="Password", font=NORM_FONT)
        e1 = ttk.Entry(self)
        e1.insert(0, "joao.rribas@gmail.com")
        e2 = ttk.Entry(self, show="*")
        e2.insert(0, "192837465jr")
        c1 = ttk.Checkbutton(self, text="Hide password", onvalue=True, offvalue=False,
                             command=lambda: toggle_password(c1, e2))

        c1.var = tk.BooleanVar(value=True)
        c1['variable'] = c1.var

        b1 = ttk.Button(self, text="Login", command=lambda: self.login(e1, e2))

        l1.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        l2.grid(row=3, column=1, padx=2, pady=2)
        l3.grid(row=4, column=1, padx=2, pady=2)
        c1.grid(row=4, column=3, padx=2, pady=2)
        e1.grid(row=3, column=2, padx=2, pady=2)
        e2.grid(row=4, column=2, padx=2, pady=2)
        b1.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)

    def login(self, e1, e2):

        global device1

        user = e1.get()
        passw = e2.get()

        httphandler = MerossHttpClient(email=user, password=passw)
        devices = httphandler.list_supported_devices()

        for counter, device in enumerate(devices):
            device1 = device

        self.master.switch_frame(GraphPage)


class GraphPage(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=10, rowspan=5, sticky=N+S+E+W)
        canvas.draw()

        toolbarframe = tk.Frame(self)
        toolbarframe.grid(row=6, column=0, columnspan=10, sticky=W)
        toolbar = CustomToolbar(canvas, toolbarframe)

        toolbar.update()

        ani = animation.FuncAnimation(fig, animate, interval=10000)

        canvas.draw()


if __name__ == "__main__":

    app = SampleApp()
    app.geometry("1024x512")
    app.mainloop()
