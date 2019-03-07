import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
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
style.use("ggplot")

################################################

date = [dt.datetime.now()]
power = [0]
currentA = [0]
currentmA = [0]
voltage = [0]
device1 = None
c = 0

f = Figure(figsize=(10.66666, 5.4166666), dpi=96)
ax = f.add_subplot(3, 1, 1)
ax1 = f.add_subplot(3, 1, 2, sharex=ax)
ax2 = f.add_subplot(3, 1, 3, sharex=ax)


################################################

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

    ax.clear()
    ax1.clear()
    ax2.clear()

    ax.plot(date, power, 'r-o')
    ax1.plot(date, voltage, 'b-o')
    if electricity["electricity"]["current"] < 9999:
        ax2.plot(date, currentmA, 'g-o')
    else:
        ax2.plot(date, currentA, 'g-o')

    ax.set_xlabel("Time", fontweight='extra bold', fontsize='x-large')
    ax.set_ylabel("Power", fontweight='extra bold', fontsize='x-large')
    ax1.set_xlabel("Time", fontweight='extra bold', fontsize='x-large')
    ax1.set_ylabel("Voltage", fontweight='extra bold', fontsize='x-large')
    ax2.set_xlabel("Time", fontweight='extra bold', fontsize='x-large')
    ax2.set_ylabel("Current", fontweight='extra bold', fontsize='x-large')

    locator = mdates.AutoDateLocator(minticks=4)
    formatter = mdates.DateFormatter('%H:%M:%S')

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax1.xaxis.set_major_locator(locator)
    ax1.xaxis.set_major_formatter(formatter)
    ax2.xaxis.set_major_locator(locator)
    ax2.xaxis.set_major_formatter(formatter)

    f.autofmt_xdate()
    f.tight_layout()

################################################


class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas_, parent_):
        self.toolitems = (
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
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
        self.e1 = ttk.Entry(self)
        self.e1.insert(0, "email")
        self.e2 = ttk.Entry(self, show="*")
        self.e2.insert(0, "password")
        self.c1 = ttk.Checkbutton(self, text="Hide password", onvalue=True, offvalue=False,
                             command=lambda: self.toggle_password())

        self.c1.var = tk.BooleanVar(value=True)
        self.c1['variable'] = self.c1.var

        b1 = ttk.Button(self, text="Login", command=lambda: self.login())

        l1.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        l2.grid(row=3, column=1, padx=2, pady=2)
        l3.grid(row=4, column=1, padx=2, pady=2)
        self.c1.grid(row=4, column=3, padx=2, pady=2)
        self.e1.grid(row=3, column=2, padx=2, pady=2)
        self.e2.grid(row=4, column=2, padx=2, pady=2)
        b1.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)

    def login(self):

        global device1

        user = self.e1.get()
        passw = self.e2.get()

        httphandler = MerossHttpClient(email=user, password=passw)
        devices = httphandler.list_supported_devices()

        for counter, device in enumerate(devices):
            device1 = device

        self.master.switch_frame(GraphPage)

    def toggle_password(self):

        if self.c1.get():
            self.e2['show'] = "*"
        else:
            self.e2['show'] = ""


class GraphPage(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=10, rowspan=5, sticky=N+S+E+W)
        canvas.draw()

        toolbarframe = tk.Frame(self)
        toolbarframe.grid(row=6, column=0, columnspan=10, sticky=W)
        toolbar = CustomToolbar(canvas, toolbarframe)

        ani = animation.FuncAnimation(f, animate, interval=10000)

        canvas.draw()
        canvas.flush_events()


if __name__ == "__main__":

    app = SampleApp()
    app.geometry("1024x512")
    app.mainloop()

