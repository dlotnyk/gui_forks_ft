import tkinter
from tkinter import filedialog
from tkinter import ttk
import datetime
from typing import Set, Dict, Tuple, List, Optional
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
from logger import log_settings
from misc import SweepData, FigEnv

#  Logger definitions
app_log = log_settings()

# Variables
fig_r_X = "figure 1"
fig_r_Y = "figure 2"
figure_fit_X = "figure 3"


class ForksGUI:
    """
    Main class for launch Forks GUI
    """
    def __init__(self, master: tkinter.Tk) -> None:
        self.master = master  # main
        self.slide1 = tkinter.IntVar()
        self.slide2 = tkinter.IntVar()
        tkinter.Grid.rowconfigure(master, 0, weight=1)
        tkinter.Grid.columnconfigure(master, 0, weight=1)
        master.title("Fork feedthrough calculation")
        self.date_convert: float = 2.324243143792273  # convert time from Labview ???
        self.figures_dict: Dict = dict()  # contains object for all figures
        self.long_sd = SweepData()
        self.label = tkinter.Label(master, text="Fork Feedthrough parameters calculation")
        self.label.pack()
        self.nb = ttk.Notebook(master)
        # first tab buttons/figures
        self.tab1 = ttk.Frame(self.nb)
        self.nb.add(self.tab1, text="Wide sweep")
        self.nb.pack(expand=1, fill="both")
        self.greet_button = tkinter.Button(self.tab1, text="Open Wide Sweep", command=self.open_wide_sweep)
        self.greet_button.pack(side=tkinter.BOTTOM)
        self.figure_tab1(self.tab1, fig_r_X)
        self.figures_dict[fig_r_X].Xtype = "Frequency [Hz]"
        self.figures_dict[fig_r_X].Ytype = "X [mV]"
        self.sc1 = tkinter.Scale(self.tab1, from_=0, to=100, orient='horizontal', variable=self.slide1,
                                 command=self.update_slider_tab1, length=300, cursor="dot")
        self.sc1.pack(side=tkinter.TOP, expand=1)
        self.sc2 = tkinter.Scale(self.tab1, from_=0, to=100, orient='horizontal', variable=self.slide2,
                                 command=self.update_slider_tab1, length=300, cursor="dot")
        self.sc2.pack(side=tkinter.TOP, expand=1)
        self.figure_tab1(self.tab1, fig_r_Y)
        self.figures_dict[fig_r_Y].Xtype = "Frequency [Hz]"
        self.figures_dict[fig_r_Y].Ytype = "Y [mV]"
        self.close_button = tkinter.Button(master, text="Close", command=master.quit)
        self.close_button.pack(anchor='center')
        # second  tab
        # todo: grid layout
        self.tab2 = ttk.Frame(self.nb)
        # tkinter.Grid.rowconfigure(master, 0, weight=1)
        # tkinter.Grid.columnconfigure(master, 0, weight=1)
        self.tab2.grid(row=0, column=0, sticky="nsew")
        self.nb.add(self.tab2, text="Short sweep")
        self.nb.pack(fill="both")
        self.figure_tab2(self.tab2, figure_fit_X, 1, 0)
        # sc2 = tkinter.Scale(self.tab2, from_=0, to=1, orient='horizontal')
        # sc2.grid(row=5, column=0, sticky="nsew")

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
            self.long_sd.create_data(data)
            self.plot_fig_tab1(self.long_sd.Frequency, self.long_sd.X, "figure 1")
            self.plot_fig_tab1(self.long_sd.Frequency, self.long_sd.Y, "figure 2")
            self.long_sd.create_mask()
            self.sc1.configure(to=self.long_sd.max_slider)
            self.sc2.configure(to=self.long_sd.max_slider)
            self.sc1.set(int(self.long_sd.max_slider / 2))
            self.sc2.set(int(self.long_sd.max_slider / 2))

    def figure_tab1(self, area: ttk.Frame, figure_key: str) -> None:
        """
        Creates an empty figure in matplotlib
        Defines sizes and another settings
        :param area: Area where figure will be build
        :param figure_key: figure key in dictionary figure list
        """
        try:
            self.figures_dict.update({figure_key: FigEnv()})
            self.figures_dict[figure_key].figure = Figure(figsize=(3, 3), dpi=100)
            self.figures_dict[figure_key].axes = self.figures_dict[figure_key].figure.add_subplot(111)
            self.figures_dict[figure_key].canvas = FigureCanvasTkAgg(self.figures_dict[figure_key].figure, master=area)
            self.figures_dict[figure_key].canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
            # self.figures_dict[figure_key].canvas.get_tk_widget().pack(side=tkinter.TOP, expand=1)
            self.figures_dict[figure_key].canvas.draw()
            app_log.info(f"`{figure_key}` canvas was successfully created")
        except Exception as ex:
            app_log.error(f"`{figure_key}` was not created due to {ex}")

    def plot_fig_tab1(self, x: np.ndarray, y: np.ndarray, figure_key: str) -> None:
        """
        Plots figure in canvas. Also sets main `axes` properties for each figure
        :param x: X - array to plot
        :param y: Y - array to plot
        :param figure_key: key of figure took from the very top of this file
        """
        try:
            if self.long_sd.Time is not None:
                utctotime = datetime.datetime.utcfromtimestamp(self.long_sd.Time[0] / self.date_convert)
                date1 = str(utctotime.date())
            else:
                date1 = ""
            self.figures_dict[figure_key].axes.clear()
            self.figures_dict[figure_key].scat = self.figures_dict[figure_key].axes.scatter(x, y, s=5)
            # self.figures_dict[figure_key].axes.plot(x, y, color='red')
            self.figures_dict[figure_key].axes.set_title(f"Wide sweep at {date1}")
            self.figures_dict[figure_key].axes.set_xlabel(self.figures_dict[figure_key].Xtype)
            self.figures_dict[figure_key].axes.set_ylabel(self.figures_dict[figure_key].Ytype)
            self.figures_dict[figure_key].axes.set_xlim(min(x), max(x))
            self.figures_dict[figure_key].axes.set_ylim(min(y), max(y))
            self.figures_dict[figure_key].axes.grid()
            self.figures_dict[figure_key].canvas.draw()
            app_log.info(f"`{figure_key}` raw data were plotted")
        except Exception as ex:
            app_log.error(f"`{figure_key}` was not updated due to: {ex}")

    def figure_tab2(self, area: ttk.Frame, figure_key: str, row: int, col: int) -> None:
        """
        figure in matplotlib
        :param area: Area where figure will be build
        :param figure_key: figure key in dictionary figure list
        :param row: row in the grid
        :param col: column in the grid
        """
        try:
            self.figures_dict.update({figure_key: FigEnv()})
            px = self.figures_dict[figure_key].px
            py = self.figures_dict[figure_key].py
            self.figures_dict[figure_key].figure = Figure(figsize=(4, 4), dpi=100)
            self.figures_dict[figure_key].axes = self.figures_dict[figure_key].figure.add_subplot(111)
            self.figures_dict[figure_key].canvas = FigureCanvasTkAgg(self.figures_dict[figure_key].figure, master=area)
            # self.figures_dict[figure_key].canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
            # self.figures_dict[figure_key].canvas.get_tk_widget().pack(side=tkinter.TOP, expand=1)
            self.figures_dict[figure_key].canvas.get_tk_widget().grid(row=row, column=col, sticky="nsew")
            self.figures_dict[figure_key].canvas.draw()
            app_log.info(f"`{figure_key}` canvas was successfully created")
        except Exception as ex:
            app_log.error(f"`{figure_key}` was not created due to {ex}")

    def update_slider_tab1(self, value):
        """
        Initiates upon updating of scales/sliders on the tab1, i.e. Open wide sweep
        """
        var1 = self.slide1.get()
        var2 = self.slide2.get()
        try:
            if self.long_sd.Frequency.any() and self.long_sd.mask.any() \
                    and self.long_sd.X.any() and self.long_sd.Y.any():
                if var2 > var1:
                    self.long_sd.mask[0:var1] = True
                    self.long_sd.mask[var2:-1] = True
                    self.long_sd.mask[var1:var2] = False
                else:
                    self.long_sd.mask[0:-1] = True
                self.figures_dict[fig_r_X].scat.remove()
                self.figures_dict[fig_r_Y].scat.remove()
                self.figures_dict[fig_r_X].scat = \
                    self.figures_dict[fig_r_X].axes.scatter(self.long_sd.Frequency[self.long_sd.mask],
                                                            self.long_sd.X[self.long_sd.mask], s=5, c="blue")
                self.figures_dict[fig_r_Y].scat = \
                    self.figures_dict[fig_r_Y].axes.scatter(self.long_sd.Frequency[self.long_sd.mask],
                                                            self.long_sd.Y[self.long_sd.mask], s=5, c="blue")
                self.figures_dict[fig_r_X].canvas.draw()
                self.figures_dict[fig_r_Y].canvas.draw()
        except Exception as ex:
            app_log.error(f"Update slider fails: {ex}")


if __name__ == "__main__":
    app_log.info("Application has started")
    root = tkinter.Tk()
    my_gui = ForksGUI(root)
    root.mainloop()
    app_log.info("Application has finished")
