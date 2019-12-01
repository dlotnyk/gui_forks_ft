import tkinter
from tkinter import filedialog
from tkinter import ttk
import logging
from logging.handlers import RotatingFileHandler
import datetime
from typing import Set, Dict, Tuple, List, Optional
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np

#  Logger definitions
log_formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(funcName)s line:(%(lineno)d) %(message)s')
logFile = "app.log"
my_handler = RotatingFileHandler(logFile, mode="a", maxBytes=2*1024*1024, backupCount=2, encoding=None, delay=False)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)
app_log = logging.getLogger("ForksFT")
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)
app_log.addHandler(console_handler)

# Variables
figure_raw_X = "figure 1"
figure_raw_Y = "figure 2"


class SweepData(object):
    """
    class contains and transforms data from .dat file into np.arrays

    :param X: X [mV] - value from lockin
    :param Y: Y [mV] - value from lockin
    :param Amplitude: X*X + Y*Y  - value from lockin
    :param Frequency: fr [Hz] - value from lockin
    :param Time: UTC time from Labview. really strange. has to apply a conversion factor
    """
    def __init__(self):
        self.X: Optional[np.ndarray] = None
        self.Y: Optional[np.ndarray] = None
        self.Amplitude: Optional[np.ndarray] = None
        self.Frequency: Optional[np.ndarray] = None
        self.Time: Optional[np.ndarray] = None
        self.pid: Optional[np.ndarray] = None

    def create_data(self, data: np.ndarray) -> None:
        """
        Parse the main data array into separate coordinates.
        :param data: Data array (Time, Frequency, X, Y, Amplitude, id)
        """
        first = True
        for idx, item in enumerate(data):
            if first:
                self.Time = np.array(item[0])
                self.Frequency = np.array(item[1])
                self.X = np.array(item[2])
                self.Y = np.array(item[3])
                self.Amplitude = np.array(item[4])
                self.pid = np.array(idx)
                first = False
            else:
                self.Time = np.append(self.Time, item[0])
                self. Frequency = np.append(self.Frequency, item[1])
                self.X = np.append(self.X, item[2])
                self.Y = np.append(self.Y, item[3])
                self.Amplitude = np.append(self.Amplitude, item[4])
                self.pid = np.append(self.pid, idx)
        else:
            app_log.info("Sweep data were created")


class FigEnv(object):
    """
    Class for Figure environment settings: Canvas, Figure, axes
    Stores figure settings of canvas (tkinter) and matplotlib attributes.
    :param __canvas: tkinter functionality for placing in the correct place.
    :param __figure: matplotlib main figure property
    :param __axes: matplotlib axes object
    :param __Xtype: type of X axis used for set_xlabel
    :param __Ytype: type of Y axis used for set_ylabel
    """
    def __init__(self):
        self.__canvas = None
        self.__figure = None
        self.__axes = None
        self.__Xtype = None
        self.__Ytype = None

    @property
    def canvas(self):
        return self.__canvas

    @canvas.setter
    def canvas(self, value):
        self.__canvas = value

    @property
    def figure(self):
        return self.__figure

    @figure.setter
    def figure(self, figure):
        self.__figure = figure

    @property
    def axes(self):
        return self.__axes

    @axes.setter
    def axes(self, axes):
        self.__axes = axes

    @property
    def Xtype(self):
        return self.__Xtype

    @Xtype.setter
    def Xtype(self, xtype):
        self.__Xtype = xtype

    @property
    def Ytype(self):
        return self.__Ytype

    @Ytype.setter
    def Ytype(self, ytype):
        self.__Ytype = ytype


class ForksGUI:
    """
    Main class for launch Forks GUI
    """
    def __init__(self, master: tkinter.Tk) -> None:
        self.master = master  # main
        master.title("Fork feedthrough caclulation")
        self.date_convert: float = 2.324243143792273  # convert time from Labview ???
        self.figures_dict: Dict = dict()  # contains object for all figures
        self.long_sweep_data = SweepData()
        self.label = tkinter.Label(master, text="Fork Feedthrough parameters calculation")
        self.label.pack()
        self.nb = ttk.Notebook(master)
        self.tab1 = ttk.Frame(self.nb)
        self.nb.add(self.tab1, text="Initialization")
        self.nb.pack(expand=1, fill="both")

        self.greet_button = tkinter.Button(self.tab1, text="Open Wide Sweep", command=self.open_wide_sweep)
        self.greet_button.pack(side=tkinter.BOTTOM)
        self.figure_tab1(self.tab1, figure_raw_X)
        self.figures_dict[figure_raw_X].Xtype = "Frequency [Hz]"
        self.figures_dict[figure_raw_X].Ytype = "X [mV]"
        self.figure_tab1(self.tab1, figure_raw_Y)
        self.figures_dict[figure_raw_Y].Xtype = "Frequency [Hz]"
        self.figures_dict[figure_raw_Y].Ytype = "Y [mV]"

        self.close_button = tkinter.Button(master, text="Close", command=master.quit)
        self.close_button.pack(side=tkinter.BOTTOM)
        self.tab2 = ttk.Frame(self.nb)
        self.nb.add(self.tab2, text="dnit")
        self.nb.pack(expand=1, fill="both")

    def open_wide_sweep(self) -> None:
        """
        Open wide sweep data. Parse and save to DataSweep object
        :return:
        """
        file1 = filedialog.askopenfilename(title="Open wide sweep file",
                                           filetypes=(("dat files", "*.dat"),
                                                      ("all files", "*.*")))
        kerneldt = np.dtype({"names": ["uni_time", "frequency", "X", "Y", "amplitude", "id"],
                             "formats": [np.longlong, np.int, float, float, float, np.int]})
        first_data = True
        try:
            app_log.info(f"File `{file1}` was successfully opened")
            with open(file1, "r") as f:
                for line in f:
                    if line[0] != "#":  # skip header
                        parse: Tuple = tuple([float(x) for x in line.split()])
                        if first_data:
                            data = np.array([parse], dtype=kerneldt)
                            first_data = False
                        else:
                            row = np.array([parse], dtype=kerneldt)
                            data = np.concatenate((data, row))
                app_log.debug(f"Shape of array is {np.shape(data)}")
        except AttributeError:
            app_log.critical(f"File does not contain an appropriate data or empty")
            raise ValueError("No data file was created. Check the file")
        except Exception as ex:
            app_log.error(f"Error while file open {ex}")
            raise ValueError("No data was created")
        else:
            app_log.info("File was parsed")
            self.long_sweep_data.create_data(data)
            self.plot_fig_tab1(self.long_sweep_data.Frequency, self.long_sweep_data.X, "figure 1")
            self.plot_fig_tab1(self.long_sweep_data.Frequency, self.long_sweep_data.Y, "figure 2")

    def figure_tab1(self, area: ttk.Frame, figure_key: str) -> None:
        """
        figure in matplotlib
        :param area: Area where figure will be build
        :param figure_key: figure key in dictionary figure list
        """
        try:
            self.figures_dict.update({figure_key: FigEnv()})
            self.figures_dict[figure_key].figure = Figure(figsize=(5, 4), dpi=100)
            self.figures_dict[figure_key].axes = self.figures_dict[figure_key].figure.add_subplot(111)
            self.figures_dict[figure_key].canvas = FigureCanvasTkAgg(self.figures_dict[figure_key].figure, master=area)
            self.figures_dict[figure_key].canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
            self.figures_dict[figure_key].canvas.draw()
            app_log.info(f"`{figure_key}` canvas was successfully created")
        except Exception as ex:
            app_log.error(f"`{figure_key}` was not created due to {ex}")

    def plot_fig_tab1(self, x, y, figure_key):
        try:
            utctotime = datetime.datetime.utcfromtimestamp(self.long_sweep_data.Time[0] / self.date_convert)
            date1 = str(utctotime.date())
            self.figures_dict[figure_key].axes.clear()
            self.figures_dict[figure_key].axes.scatter(x, y)
            self.figures_dict[figure_key].axes.plot(x, y, color='red')
            self.figures_dict[figure_key].axes.set_title(f"Wide sweep at {date1}")
            self.figures_dict[figure_key].axes.set_xlabel(self.figures_dict[figure_key].Xtype)
            self.figures_dict[figure_key].axes.set_ylabel(self.figures_dict[figure_key].Ytype)
            self.figures_dict[figure_key].axes.set_xlim(min(x), max(x))
            self.figures_dict[figure_key].axes.set_ylim(min(y), max(y))
            self.figures_dict[figure_key].axes.grid()
            self.figures_dict[figure_key].axes.plot()
            self.figures_dict[figure_key].canvas.draw()
            app_log.info(f"`{figure_key}` was updated")
        except Exception as ex:
            app_log.error(f"`{figure_key}` was not updated due to: {ex}")


if __name__ == "__main__":
    app_log.info("Application has started")
    root = tkinter.Tk()
    my_gui = ForksGUI(root)
    root.mainloop()
    app_log.info("Application has finished")
