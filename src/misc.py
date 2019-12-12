import numpy as np
from typing import Set, Dict, Tuple, List, Optional, NamedTuple
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.collections import PathCollection
from logger import log_settings

#logger
app_log = log_settings()


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
        self.mask: Optional[np.ndarray] = None
        self.dx: Optional[np.ndarray] = None
        self.dy: Optional[np.ndarray] = None
        # app_log = log_settings()
        self.slider1: int = 0
        self.slider2: int = 1
        self.max_slider: int = 0
        self.group: Optional[str] = None

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

    def update_deltax(self, delta: np.ndarray):
        self.dx = delta

    def update_deltay(self, delta: np.ndarray):
        self.dy = delta

    def create_mask(self) -> None:
        """
        Create a bool mask after importing a dat file.
        """
        if self.Frequency is not None:
            self.mask = np.ones(len(self.Frequency), dtype=bool)
            self.slider1 = 0
            self.slider2 = len(self.Frequency) - 1
            self.max_slider = len(self.Frequency) - 1
            app_log.info("mask was created")
        else:
            app_log.warning("You should import a data file first")

    def update_y_tail(self, idm: np.ndarray, delta: float) -> None:
        """
        FIxes the Y tail and updates whole Y array
        :param idm: Index of the jump value
        :param delta: Jump of the Y value
        :num: points to cut around jump
        """
        num = 10
        if (self.Y is not None) and (self.Frequency is not None):
            try:
                part1 = np.add(self.Y[0:idm], delta)
                self.Y = np.concatenate((part1, self.Y[idm:]))
            except Exception as ex:
                app_log.error(f"y-tail fails: {ex}")
            else:
                app_log.info(f"ytail concentrated {len(self.Frequency)} vs {len(self.Y)}")


class FigEnv(object):
    """
    Class for Figure environment settings: Canvas, Figure, axes
    Stores figure settings of canvas (tkinter) and matplotlib attributes.
    :param __canvas: tkinter functionality for placing in the correct place.
    :param __figure: matplotlib main figure property
    :param __axes: matplotlib axes object
    :param __Xtype: type of X axis used for set_xlabel
    :param __Ytype: type of Y axis used for set_ylabel
    :param __px: x-grid dimensions for layout
    :param __py: y-grid dimensions for layout
    :param __scat: scatter object for plot (raw)
    :param __pltt: plot object for plot (fit)
    :param __polk: group attribute, Wide, Short, maybe fit. etc
    """
    def __init__(self):
        self.__canvas: Optional[FigureCanvasTkAgg] = None
        self.__figure: Optional[Figure] = None
        self.__axes: Optional[Figure.axes] = None
        self.__Xtype: Optional[str] = None
        self.__Ytype: Optional[str] = None
        self.__px: int = 5
        self.__py: int = 4
        self.__scat: Optional[PathCollection] = None
        self.__pltt: Optional[PathCollection] = None

    @property
    def canvas(self) -> FigureCanvasTkAgg:
        return self.__canvas

    @canvas.setter
    def canvas(self, value: FigureCanvasTkAgg) -> None:
        self.__canvas = value

    @property
    def figure(self):
        return self.__figure

    @figure.setter
    def figure(self, figure: Figure):
        self.__figure = figure

    @property
    def axes(self) -> Figure.axes:
        return self.__axes

    @axes.setter
    def axes(self, axes: Figure.axes) -> None:
        self.__axes = axes

    @property
    def Xtype(self) -> Optional[str]:
        return self.__Xtype

    @Xtype.setter
    def Xtype(self, xtype: str) -> None:
        self.__Xtype = xtype

    @property
    def Ytype(self) -> Optional[str]:
        return self.__Ytype

    @Ytype.setter
    def Ytype(self, ytype: str) -> None:
        self.__Ytype = ytype

    @property
    def px(self) -> int:
        return self.__px

    @px.setter
    def px(self, px: int) -> None:
        self.__px = px

    @property
    def py(self) -> int:
        return self.__py

    @py.setter
    def py(self, py: int) -> None:
        self.__py = py

    @property
    def scat(self) -> PathCollection:
        return self.__scat

    @scat.setter
    def scat(self, scat: PathCollection) -> None:
        self.__scat = scat

    @property
    def pltt(self) -> PathCollection:
        return self.__pltt

    @pltt.setter
    def pltt(self, pltt: PathCollection) -> None:
        self.__pltt = pltt


class FigureGroup(NamedTuple):
    """
    Grouping of figures into wide, short ones
    Attributes:
        :param name: name of group
        :param x: raw X
        :param y: raw Y
        :param fit_x: background X
        :param fit_y: background Y
    """
    name: str
    x: str
    y: str
    sub_x: str
    sub_y: str


class FitParams:
    """
    Contains all necessary fitting parameters and method to access/change those
    """
    def __init__(self):
        self.__fitx: Optional[np.ndarray] = None
        self.__fity: Optional[np.ndarray] = None

    @property
    def fitx(self) -> np.ndarray:
        return self.__fitx

    @fitx.setter
    def fitx(self, vals: np.ndarray) -> None:
        self.__fitx = vals

    @property
    def fity(self) -> np.ndarray:
        return self.__fity

    @fity.setter
    def fity(self, vals: np.ndarray) -> None:
        self.__fity = vals

    def update_slope_x(self, val: float) -> None:
        """
        Update slope of X fit parameter by value val.
        :param val: increment to add
        """
        try:
            if self.__fitx is not None:
                old = self.__fitx
                self.__fitx[-2] += val
                new = self.__fitx
                if np.array_equal(old, new):
                    app_log.info("New slope is set")
                else:
                    app_log.info("Slope has NOT been changed")
        except Exception as ex:
            app_log.error(f"Can not change slope x: {ex}")

    def update_intersect_x(self, val: float) -> None:
        """
        Updates the intersect of X fit parameter by value val.
        :param val: increment to change the intersect of fit X
        """
        try:
            if self.__fitx is not None:
                self.__fitx[-1] += val
        except Exception as ex:
            app_log.error(f"Can not change intersect X: {ex}")


