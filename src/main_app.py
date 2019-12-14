import tkinter
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import datetime
from typing import Set, Dict, Tuple, List, Optional
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
import scipy.signal as sci
from scipy.optimize import curve_fit

from logger import log_settings
from misc import SweepData, FigEnv, FigureGroup, FitParams, Mediator, Base, TextsMan

#  Logger definitions
app_log = log_settings()

# Variables
poly_x = 3
poly_y = 4
fits = FitParams()
long_sd = SweepData()
short_sd = SweepData()
fig_r_X = "figure 1"
fig_r_Y = "figure 2"
figure_fit_X = "figure 3"
fig_d_X = "figure 4"
fig_d_Y = "figure 5"
fig_sh_sw_X = "figure 6"
fig_sh_sw_Y = "figure 7"
fig_sh_d_X = "figure 8"
fig_sh_d_Y = "figure 9"
fig_theory_x = "figure 10"
fig_wide = FigureGroup("wide", fig_r_X, fig_r_Y, fig_d_X, fig_d_Y)
fig_short = FigureGroup("short", fig_sh_sw_X, fig_sh_sw_Y, fig_sh_d_X, fig_sh_d_Y)
fit_str = ("x0 = ", "x1 = ", "x2 = ", "x3 = ", "y0 = ", "y1 = ", "y2 = ", "y3 = ", "y4 = ", "f0 = ", "Q = ", "K = ")
# fit_str = ("x0 = ", "x1 = ", "x2 = ", "x3 = ", "y1 = ", "y2 = ", "y3 = ", "y4 = ")


# class UpdateFitText(Mediator):
#     def __init__(self, component1: ForksGUI, ):


class ForksGUI(Base):
    """
    Main class for launch Forks GUI
    """
    def __init__(self, master: tkinter.Tk) -> None:
        super().__init__()
        self.master = master  # main
        self.slide1 = tkinter.IntVar()
        self.slide2 = tkinter.IntVar()
        tkinter.Grid.rowconfigure(master, 0, weight=1)
        tkinter.Grid.columnconfigure(master, 0, weight=1)
        master.title("Fork feedthrough calculation")
        self.date_convert: float = 2.324243143792273  # convert time from Labview ???
        self.figures_dict: Dict = dict()  # contains object for all figures
        self.label = tkinter.Label(master, text="Fork Feedthrough parameters calculation")
        self.label.pack()
        self.nb = ttk.Notebook(master)

        # first tab buttons/figures is long sweep raw
        self.tab1 = ttk.Frame(self.nb)
        self.nb.add(self.tab1, text="Wide sweep")
        self.nb.pack(expand=1, fill="both")
        self.fit_button = tkinter.Button(self.tab1, text="Fit the Wide Sweep", command=self.fit_wide_sweep)
        self.fit_button.pack(side=tkinter.BOTTOM)
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

        # third tab. Long sweep subtract
        self.tab3 = ttk.Frame(self.nb)
        self.nb.add(self.tab3, text="Substraction of the wide sweep")
        self.nb.pack(expand=1, fill="both")
        self.figure_tab1(self.tab3, fig_d_X)
        self.figures_dict[fig_d_X].Xtype = "Frequency [Hz]"
        self.figures_dict[fig_d_X].Ytype = "X - fitX [mV]"
        self.figure_tab1(self.tab3, fig_d_Y)
        self.figures_dict[fig_d_Y].Xtype = "Frequency [Hz]"
        self.figures_dict[fig_d_Y].Ytype = "Y - fitY [mV]"

        # fourth tab buttons/figures. Short sweep raw
        self.tab4 = ttk.Frame(self.nb)
        self.nb.add(self.tab4, text="Short sweep")
        self.nb.pack(expand=1, fill="both")
        self.oss_button = tkinter.Button(self.tab4, text="Open Short Sweep", command=self.open_short_sweep)
        self.oss_button.pack(side=tkinter.BOTTOM)
        self.refr_button = tkinter.Button(self.tab4, text="Refresh", command=lambda: self.plot_subtr(short_sd))
        self.refr_button.pack(side=tkinter.BOTTOM)
        self.ytail_button = tkinter.Button(self.tab4, text="Fix Y tail", command=self.fix_y_tail)
        self.ytail_button.pack(side=tkinter.BOTTOM)
        self.figure_tab1(self.tab4, fig_sh_sw_X)
        self.figures_dict[fig_sh_sw_X].Xtype = "Frequency [Hz]"
        self.figures_dict[fig_sh_sw_X].Ytype = "X [mV]"
        self.figure_tab1(self.tab4, fig_sh_sw_Y)
        self.figures_dict[fig_sh_sw_Y].Xtype = "Frequency [Hz]"
        self.figures_dict[fig_sh_sw_Y].Ytype = "Y [mV]"

        # fifth tab buttons/figures. Short sweep subtract
        self.tab5 = ttk.Frame(self.nb)
        self.nb.add(self.tab5, text="Short sweep substr")
        self.nb.pack(expand=1, fill="both")
        self.fixx_button = tkinter.Button(self.tab5, text="Slope X", command=self.fix_slope_x)
        self.fixx_button.pack(side=tkinter.BOTTOM)
        self.interx_button = tkinter.Button(self.tab5, text="Intersect X", command=self.fix_intesect_x)
        self.interx_button.pack(side=tkinter.BOTTOM)
        self.intery_button = tkinter.Button(self.tab5, text="Intersect Y", command=self.fix_intersect_y)
        self.intery_button.pack(side=tkinter.BOTTOM)
        self.fitall_button = tkinter.Button(self.tab5, text="Fit both channels", command=self.fit_both_curves)
        self.fitall_button.pack(side=tkinter.BOTTOM)
        self.figure_tab1(self.tab5, fig_sh_d_X)
        self.figures_dict[fig_sh_d_X].Xtype = "Frequency [Hz]"
        self.figures_dict[fig_sh_d_X].Ytype = "X [mV]"
        self.figure_tab1(self.tab5, fig_sh_d_Y)
        self.figures_dict[fig_sh_d_Y].Xtype = "Frequency [Hz]"
        self.figures_dict[fig_sh_d_Y].Ytype = "Y [mV]"

        # sixth tab. Circle X vs Y
        self.tab6 = ttk.Frame(self.nb)
        self.nb.add(self.tab6, text=" Circle X vs Y")
        self.nb.pack(expand=1, fill="both")
        self.figure_tab2(self.tab6, fig_theory_x, 1, 1)
        self.figures_dict[fig_theory_x].Xtype = "X [mV]"
        self.figures_dict[fig_theory_x].Ytype = "Y [mV]"

        # seventh tab. Text with fit parameters
        self.tab7 = ttk.Frame(self.nb)
        self.nb.add(self.tab7, text="Fit parameters")
        self.nb.pack(expand=1, fill="both")
        self.fit_text = tkinter.Text(self.tab7, height=12, width=60)
        self.fit_text.pack(side=tkinter.TOP)
        self.fit_text.insert(tkinter.END, "\n".join(fit_str))

        app_log.info("All tabs were initialized")
        messagebox.showinfo("Manual", TextsMan.manual)

    @staticmethod
    def open_file(sweep: str) -> np.ndarray:
        """
        Open wide or short sweep data. Parse and save to DataSweep object.
        :param sweep:
        :return data: An np.array with parsed data
        :raise: ValueError
        """
        file1 = filedialog.askopenfilename(title="Open " + sweep + " file",
                                           filetypes=(("dat files", "*.dat"),
                                                      ("all files", "*.*")))
        kerneldt = np.dtype({"names": ["uni_time", "frequency", "X", "Y", "amplitude", "id"],
                             "formats": [np.longlong, np.int, float, float, float, np.int]})
        first_data = True
        try:
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
            messagebox.showerror("Error", "File does not contain an appropriate data or empty")
            raise ValueError("No data file was created. Check the file")
        except Exception as ex:
            app_log.error(f"File can NOT be opened: {ex}")
            messagebox.showerror("Error", f"File can NOT be opened: {ex}")
            raise ValueError("No data was created")
        else:
            app_log.info(f"File: {file1} was parsed")
            return data

    def open_wide_sweep(self) -> None:
        """
        Open wide sweep data. Parse and save to DataSweep object
        :return:
        """
        try:
            data = self.open_file("wide")
            long_sd.create_data(data)
            self.plot_fig_tab1(long_sd.Frequency, long_sd.X, fig_r_X)
            self.plot_fig_tab1(long_sd.Frequency, long_sd.Y, fig_r_Y)
            long_sd.create_mask()
            long_sd.group = "wide"
            self.sc1.configure(to=long_sd.max_slider)
            self.sc2.configure(to=long_sd.max_slider)
            self.sc1.set(int(long_sd.max_slider / 2))
            self.sc2.set(int(long_sd.max_slider / 2))
        except Exception as ex:
            app_log.warning(f"Open of wide sweep fails cause of: {ex}")
        else:
            app_log.info("Wide sweep is opened and parsed")

    def open_short_sweep(self) -> None:
        """
        Open short sweep data. Parse and save to DataSweep object
        :return:
        """
        try:
            data = self.open_file("short")
            short_sd.create_data(data)
            self.plot_fig_tab1(short_sd.Frequency, short_sd.X, fig_sh_sw_X)
            self.plot_fig_tab1(short_sd.Frequency, short_sd.Y, fig_sh_sw_Y)
            short_sd.create_mask()
            short_sd.group = "short"
            self.plot_subtr(short_sd)
        except Exception as ex:
            app_log.warning(f"Open of wide sweep fails cause of: {ex}")
        else:
            app_log.info("Short sweep is opened and parsed")

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
            self.figures_dict[figure_key].canvas.draw()
            app_log.info(f"`{figure_key}` canvas was successfully created")
        except Exception as ex:
            messagebox.showerror("Error", f"Figure {figure_key} can NOT be created: {ex}")
            app_log.error(f"`{figure_key}` was not created due to {ex}")

    def plot_fig_tab1(self, x: np.ndarray, y: np.ndarray, figure_key: str) -> None:
        """
        Plots figure in canvas. Also sets main `axes` properties for each figure
        :param x: X - array to plot
        :param y: Y - array to plot
        :param figure_key: key of figure took from the very top of this file
        """
        try:
            if long_sd.Time is not None:
                utctotime = datetime.datetime.utcfromtimestamp(long_sd.Time[0] / self.date_convert)
                date1 = str(utctotime.date())
            else:
                date1 = ""
            self.figures_dict[figure_key].axes.clear()
            self.figures_dict[figure_key].scat = self.figures_dict[figure_key].axes.scatter(x, y, s=5)
            self.figures_dict[figure_key].axes.set_title(f" {figure_key}: Wide sweep at {date1}")
            self.figures_dict[figure_key].axes.set_xlabel(self.figures_dict[figure_key].Xtype)
            self.figures_dict[figure_key].axes.set_ylabel(self.figures_dict[figure_key].Ytype)
            self.figures_dict[figure_key].axes.set_xlim(min(x), max(x))
            self.figures_dict[figure_key].axes.set_ylim(min(y), max(y))
            self.figures_dict[figure_key].axes.grid()
            self.figures_dict[figure_key].canvas.draw()
            app_log.info(f"`{figure_key}` raw data were plotted")
        except Exception as ex:
            app_log.error(f"`{figure_key}` was not updated due to: {ex}")
            messagebox.showerror("Error", f"Figure {figure_key} can NOT be Updated: {ex}")

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
            # px = self.figures_dict[figure_key].px
            # py = self.figures_dict[figure_key].py
            self.figures_dict[figure_key].figure = Figure(figsize=(6, 6), dpi=100)
            self.figures_dict[figure_key].axes = self.figures_dict[figure_key].figure.add_subplot(111)
            self.figures_dict[figure_key].axes.set_title(f" {figure_key}: X vs Y")
            self.figures_dict[figure_key].canvas = FigureCanvasTkAgg(self.figures_dict[figure_key].figure, master=area)
            self.figures_dict[figure_key].canvas.get_tk_widget().grid(row=row, column=col, sticky="nsew")
            self.figures_dict[figure_key].canvas.draw()
            app_log.info(f"`{figure_key}` canvas was successfully created")
        except Exception as ex:
            messagebox.showerror("Error", f"Figure {figure_key} can NOT be created: {ex}")
            app_log.error(f"`{figure_key}` was not created due to {ex}")

    def update_slider_tab1(self, value) -> None:
        """
        Initiates upon updating of scales/sliders on the tab1, i.e. Open wide sweep
        """
        var1 = self.slide1.get()
        var2 = self.slide2.get()
        try:
            if long_sd.Frequency is not None and long_sd.mask is not None \
                    and long_sd.X is not None and long_sd.Y is not None:
                if var2 > var1:
                    long_sd.mask[0:var1] = True
                    long_sd.mask[var2:-1] = True
                    long_sd.mask[var1:var2] = False
                else:
                    long_sd.mask[0:-1] = True
                self.figures_dict[fig_r_X].scat.remove()
                self.figures_dict[fig_r_Y].scat.remove()
                self.figures_dict[fig_r_X].scat = \
                    self.figures_dict[fig_r_X].axes.scatter(long_sd.Frequency[long_sd.mask],
                                                            long_sd.X[long_sd.mask], s=10, c="blue")
                self.figures_dict[fig_r_Y].scat = \
                    self.figures_dict[fig_r_Y].axes.scatter(long_sd.Frequency[long_sd.mask],
                                                            long_sd.Y[long_sd.mask], s=10, c="blue")
                self.figures_dict[fig_r_X].canvas.draw()
                self.figures_dict[fig_r_Y].canvas.draw()
        except Exception as ex:
            app_log.error(f"Update slider fails: {ex}")

    def fit_wide_sweep(self) -> None:
        """
        Fit the wide sweep. X with poly of 3, Y with poly of 4. Using mask
        """
        try:
            if long_sd.Frequency is not None and long_sd.mask is not None \
                    and long_sd.X is not None and long_sd.Y is not None:

                fits.fitx = np.polyfit(long_sd.Frequency[long_sd.mask],
                                   long_sd.X[long_sd.mask], poly_x)
                fits.fity = np.polyfit(long_sd.Frequency[long_sd.mask],
                                   long_sd.Y[long_sd.mask], poly_y)
                r_fit_x = np.poly1d(fits.fitx)
                r_fit_y = np.poly1d(fits.fity)
                if self.figures_dict[fig_r_X].pltt:
                    self.figures_dict[fig_r_X].pltt.remove()
                self.figures_dict[fig_r_X].pltt = \
                    self.figures_dict[fig_r_X].axes.scatter(long_sd.Frequency,
                                                            r_fit_x(long_sd.Frequency), c="red", s=1)
                self.figures_dict[fig_r_X].axes.set_ylim(min(r_fit_x(long_sd.Frequency)),
                                                         max(r_fit_x(long_sd.Frequency)))
                self.figures_dict[fig_r_X].canvas.draw()
                if self.figures_dict[fig_r_Y].pltt:
                    self.figures_dict[fig_r_Y].pltt.remove()
                self.figures_dict[fig_r_Y].pltt = \
                    self.figures_dict[fig_r_Y].axes.scatter(long_sd.Frequency,
                                                            r_fit_y(long_sd.Frequency), c="red", s=1)
                self.figures_dict[fig_r_Y].axes.set_ylim(min(r_fit_y(long_sd.Frequency)),
                                                         max(r_fit_y(long_sd.Frequency)))
                self.figures_dict[fig_r_Y].canvas.draw()
                self.plot_subtr(long_sd)
                app_log.info("Fit of wide sweep was done")
        except Exception as ex:
            messagebox.showerror("Error", f"Fails to fit the wide sweep: {ex}")
            app_log.error(f"Fail to fit: {ex}")

    def plot_subtr(self, sweep: SweepData) -> None:
        """
        Plot subtraction after import wide sweep and fitting the graphs
        """
        try:
            if sweep.group is not None:
                if sweep.group == fig_wide.name:
                    fig_namex = fig_wide.sub_x
                    fig_namey = fig_wide.sub_y
                elif sweep.group == fig_short.name:
                    fig_namex = fig_short.sub_x
                    fig_namey = fig_short.sub_y
                else:
                    app_log.critical("Subtraction error. No sweep was found")
                    raise ValueError("Wide or short sweep does not found or names do not match.")
            if (sweep.X is not None) and (sweep.Y is not None) \
                    and (sweep.Frequency is not None):
                r_fit_x = np.poly1d(fits.fitx)
                r_fit_y = np.poly1d(fits.fity)
                dx = np.subtract(sweep.X, r_fit_x(sweep.Frequency))
                dy = np.subtract(sweep.Y, r_fit_y(sweep.Frequency))
                sweep.update_deltax(dx)
                sweep.update_deltay(dy)
                if self.figures_dict[fig_namex].scat is None:
                    self.figures_dict[fig_namex].axes.clear()
                    self.figures_dict[fig_namex].axes.set_title(f"{fig_namex}: Subtract of X for {sweep.group} sweep ")
                    self.figures_dict[fig_namex].axes.set_xlim(min(sweep.Frequency), max(sweep.Frequency))
                    self.figures_dict[fig_namex].axes.set_xlabel(self.figures_dict[fig_namex].Xtype)
                    self.figures_dict[fig_namex].axes.set_ylabel(self.figures_dict[fig_namex].Ytype)
                    self.figures_dict[fig_namex].axes.grid()
                else:
                    self.figures_dict[fig_namex].scat.remove()
                if sweep.dx is not None:
                    self.figures_dict[fig_namex].axes.set_ylim(min(sweep.dx), max(sweep.dx))
                    self.figures_dict[fig_namex].scat = self.figures_dict[fig_namex].axes.scatter(sweep.Frequency,
                                                                                                  sweep.dx,
                                                                                              s=5, c="green")
                self.figures_dict[fig_namex].canvas.draw()
                app_log.info(f"`{fig_namex}` subtract data were plotted")
                if self.figures_dict[fig_namey].scat is None:
                    self.figures_dict[fig_namey].axes.clear()
                    self.figures_dict[fig_namey].axes.set_title(f"{fig_namey}: Subtract of Y for {sweep.group} sweep ")
                    self.figures_dict[fig_namey].axes.set_xlabel(self.figures_dict[fig_namey].Xtype)
                    self.figures_dict[fig_namey].axes.set_ylabel(self.figures_dict[fig_namey].Ytype)
                    self.figures_dict[fig_namey].axes.set_xlim(min(sweep.Frequency), max(sweep.Frequency))
                    self.figures_dict[fig_namey].axes.grid()
                else:
                    self.figures_dict[fig_namey].scat.remove()
                if sweep.dy is not None:
                    self.figures_dict[fig_namey].axes.set_ylim(min(sweep.dy), max(sweep.dy))
                    self.figures_dict[fig_namey].scat = self.figures_dict[fig_namey].axes.scatter(sweep.Frequency,
                                                                                                  sweep.dy,
                                                                                              s=5, c="green")
                self.figures_dict[fig_namey].canvas.draw()
                app_log.info(f"`{fig_namey}` subtract data were plotted")
        except AttributeError:
            app_log.error(f"Short sweep opens before fit of the wide sweep")
            messagebox.showerror("File opens before fit", "You open a file before perform a fit of the wide sweep. "
                                                          "Please fit and click Refresh button.")
        except Exception as ex:
            app_log.error(f"Plot sub is fail: {ex}")
            messagebox.showerror("Error", f"Plot of figure is fail: {ex}")

    def fix_slope_x(self) -> None:
        """
        Fix the slope for X component.
        nums: number of points for mean function
        """
        nums = 100
        try:
            if (short_sd.dx is not None) and (short_sd.Frequency is not None):
                id0 = np.argmax(short_sd.dx)
                short_sd.ind_max = id0
                max0 = np.amax(short_sd.dx)
                d1 = len(short_sd.dx) - id0
                shift = np.minimum(id0, d1)
                part1 = short_sd.dx[(id0-shift):(id0-shift)+nums]
                part2 = short_sd.dx[(id0+shift)-nums:(id0+shift)]
                arg1 = short_sd.Frequency[(id0-shift):(id0-shift)+nums]
                arg2 = short_sd.Frequency[(id0+shift)-nums:(id0+shift)]
                p1 = np.mean(part1)
                p2 = np.mean(part2)
                x1 = np.mean(arg1)
                x2 = np.mean(arg2)
                k = (p2-p1)/(x2-x1)
                fits.update_slope_x(k)
                self.plot_subtr(short_sd)
        except Exception as ex:
            app_log.error(f"Slope of X can not be fixed: {ex}")
            messagebox.showerror("Error", f"Slope for X was NOT updated: {ex}")
        else:
            app_log.info(f"Slope for X was updated")

    def fix_intesect_x(self) -> None:
        """
        Change the intersect of X in order to move the whole graph up or down under the X-axis
        :num: Number of points from the begin and end to cut and analyze
        """
        num = 100
        try:
            if (short_sd.X is not None) and (short_sd.dx is not None):
                part1 = short_sd.dx[0:num]
                part2 = short_sd.dx[-num:-1]
                subtr = np.minimum(np.mean(part1), np.mean(part2))
                add = np.maximum(np.std(part1), np.std(part2))
                fits.update_intersect_x(subtr-add)
                self.plot_subtr(short_sd)
        except Exception as ex:
            app_log.error(f"Intersect of X can NOT be changed: {ex}")
            messagebox.showerror("Error", f"Intersection for X was NOT updated: {ex}")
        else:
            app_log.info(f"Intersect X is changed")

    def fix_y_tail(self) -> None:
        """
        Fix the jump on the short sweep in Y channel.
        :num: is used for cutting +-
        :wind:poly: window and poly value for Savitsky-Golay filtering
        """
        num = 10
        wind = 21
        poly = 1
        try:
            if (short_sd.Y is not None) and (short_sd.Frequency is not None):
                id0 = np.argmax(short_sd.Y)
                part1 = short_sd.Y[0:id0]
                dif_y = sci.savgol_filter(part1, wind, poly, deriv=1)
                prob = np.argmax(np.abs(dif_y))
                y1 = np.mean(part1[prob - 2*num: prob - num])
                y2 = np.mean(part1[prob + num: prob + 2*num])
                delta = y2-y1
                short_sd.update_y_tail(prob, delta)
                if self.figures_dict[fig_sh_sw_Y].scat is not None:
                    self.figures_dict[fig_sh_sw_Y].scat.remove()
                self.figures_dict[fig_sh_sw_Y].scat = self.figures_dict[fig_sh_sw_Y].axes.scatter(short_sd.Frequency,
                                                                                             short_sd.Y, s=10, c="blue")
                self.figures_dict[fig_sh_sw_Y].canvas.draw()
        except Exception as ex:
            app_log.error(f"Y-tail can NOT be fixed {ex}")
            messagebox.showerror("Error", f"Y-tail was NOT updated: {ex}")
        else:
            app_log.info("Y-tail is fixed")

    def fix_intersect_y(self) -> None:
        """
        Fixes an interface of the dY signal
        """
        try:
            if (short_sd.dy is not None) and (short_sd.Frequency is not None):
                id0 = np.argmax(short_sd.dy)
                max_y = short_sd.dy[id0]
                id1 = np.argmin(short_sd.dy)
                min_y = short_sd.dy[id1]
                val = (max_y + min_y)/2
                fits.update_intersect_y(val)
                self.plot_subtr(short_sd)
        except Exception as ex:
            app_log.error(f"Y-intersect can NOT be fixed: {ex}")
            messagebox.showerror("Error", f"Intersect for Y was NOT updated: {ex}")
        else:
            app_log.info(f"Y-intersect is fixed")

    def fit_both_curves(self):
        """
        Performs the fit of dX and dY
        """
        a = 10000
        q = 30.0
        try:
            if (short_sd.dy is not None) and (short_sd.Frequency is not None) and (short_sd.dx is not None):
                if short_sd.ind_max is not None:
                    f0 = short_sd.Frequency[short_sd.ind_max]
                else:
                    f0 = 32000
                p0 = [f0, q, a]
                popt, pcov = curve_fit(short_sd.fun_fit_x, short_sd.Frequency, short_sd.dx, p0, maxfev=10000,
                                       ftol=0.00005, xtol=0.00005)
                short_sd.gen_fit_x(popt[0], popt[1], popt[2])
                short_sd.gen_fit_y(popt[0], popt[1], popt[2])
                if self.figures_dict[fig_sh_d_X].pltt is not None:
                    self.figures_dict[fig_sh_d_X].pltt.remove()
                self.figures_dict[fig_sh_d_X].pltt = self.figures_dict[fig_sh_d_X].axes.scatter(short_sd.Frequency,
                                                                                                short_sd.dx_fit,
                                                                                                s=4, c="red")
                self.figures_dict[fig_sh_d_X].canvas.draw()
                if self.figures_dict[fig_sh_d_Y].pltt is not None:
                    self.figures_dict[fig_sh_d_Y].pltt.remove()
                self.figures_dict[fig_sh_d_Y].pltt = self.figures_dict[fig_sh_d_Y].axes.scatter(short_sd.Frequency,
                                                                                                short_sd.dy_fit,
                                                                                                s=4, c="red")
                self.figures_dict[fig_sh_d_Y].canvas.draw()
                fits.f0 = popt[0]
                fits.q = popt[1]
                fits.k = self.find_k()
                self.plot_circle(fig_theory_x)
        except Exception as ex:
            app_log.error(f"Can not fit: {ex}")
            messagebox.showerror("Error", f"The Short sweep fit fails: {ex}")
        else:
            app_log.info(f"Both channels were fitted")

    def plot_circle(self, figure_key: str) -> None:
        """
        Plot X vs Y as well as fitted X vs Y
        """
        try:
            if (short_sd.dx is not None) and (short_sd.dy is not None) and (short_sd.dx_fit is not None) and \
            (short_sd.dy_fit is not None):
                self.figures_dict[figure_key].axes.clear()
                self.figures_dict[figure_key].scat = self.figures_dict[figure_key].axes.scatter(short_sd.dx,
                                                                                                short_sd.dy,
                                                                                                s=10, c="blue")
                self.figures_dict[figure_key].pltt= self.figures_dict[figure_key].axes.scatter(short_sd.dx_fit,
                                                                                                short_sd.dy_fit,
                                                                                                s=5, c="red")
                self.figures_dict[figure_key].axes.set_xlabel(self.figures_dict[figure_key].Xtype)
                self.figures_dict[figure_key].axes.set_ylabel(self.figures_dict[figure_key].Ytype)
                self.figures_dict[figure_key].axes.set_xlim(min(short_sd.dx), max(short_sd.dx))
                self.figures_dict[figure_key].axes.set_ylim(min(short_sd.dy), max(short_sd.dy))
                self.figures_dict[figure_key].axes.grid()
                self.figures_dict[figure_key].canvas.draw()
        except Exception as ex:
            app_log.error(f"`{figure_key}` was not updated due to: {ex}")
            messagebox.showerror("Error", f"Circle plot was not plotted: {ex}")
        else:
            app_log.info(f"Circle in {figure_key} was plotted")

    def change_text(self):
        try:
            if fits.fitx is None:
                x_params = np.empty(poly_x+1, dtype=str)
            else:
                x_params = np.flip(fits.fitx)
            if fits.fity is None:
                y_params = np.empty(poly_y+1, dtype=str)
            else:
                y_params = np.flip(fits.fity)
            if fits.f0 is None:
                f0 = np.empty(1, dtype=str)
            else:
                f0 = fits.f0
            if fits.q is None:
                q = np.empty(1, dtype=str)
            else:
                q = fits.q
            if fits.k is None:
                k = np.empty(1, dtype=str)
            else:
                k = fits.k
            sum_arr = np.concatenate((x_params, y_params, f0, q, k))
            sum_str = "".join("{0}\t{1}\n".format(ii, jj) for ii, jj in zip(fit_str, sum_arr))
            self.fit_text.delete(1.0, tkinter.END)
            self.fit_text.insert(tkinter.END, sum_str)
        except Exception as ex:
            app_log.error(f"Fit box can NOT be updated: {ex}")
            messagebox.showerror("Error", f"Parameter Text box was NOT updated: {ex}")
        else:
            app_log.info(f"Fit box is updated")

    def find_k(self) -> Optional[float]:
        """
        Find a K - coefficient to calibrate sensitivity of locking. r = sqrt(x^2 + y^2) at resonant frequency
        r_max == drive voltage
        """
        try:
            if (short_sd.dx_fit is not None) and (short_sd.dy_fit is not None) and (fits.q is not None):
                x_m = short_sd.dx_fit.max()
                y_m = short_sd.dy_fit.max()
                val = np.sqrt(x_m**2 + y_m**2)
                val1 = fits.q*0.1/val
                k = val1[0]
            else:
                k = None
        except Exception as ex:
            app_log.error(f"Can not find K: {ex}")
            messagebox.showerror("Error", f"Can not calculate `k`: {ex}")
            return None
        else:
            app_log.info("K is found")
            return k


class ConcreteMedia(Mediator):
    """
    Makes communication between two classes: ForksGUI and FitParams
    """
    def __init__(self, component1: ForksGUI, component2: FitParams) -> None:
        self._component1 = component1
        self._component1.mediator = self
        self._component2 = component2
        self._component2.mediator = self

    def notify(self, sender, event) -> None:
        """
        FitParams sends a notification to upgrade a txt with fitting parameters while setters used.
        """
        if event == "changeparams":
            self._component1.change_text()


if __name__ == "__main__":
    app_log.info("Application has started")
    root = tkinter.Tk()
    my_gui = ForksGUI(root)
    media = ConcreteMedia(my_gui, fits)
    root.mainloop()
    app_log.info("Application has finished")
