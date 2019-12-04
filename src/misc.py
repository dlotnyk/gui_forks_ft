import numpy as np
from typing import Set, Dict, Tuple, List, Optional
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from logger import log_settings


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
        self.app_log = log_settings()

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
            self.app_log.info("Sweep data were created")


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
    """
    def __init__(self):
        self.__canvas: Optional[FigureCanvasTkAgg] = None
        self.__figure: Optional[Figure] = None
        self.__axes: Optional[Figure.axes] = None
        self.__Xtype: Optional[str] = None
        self.__Ytype: Optional[str] = None
        self.__px: int = 5
        self.__py: int = 4
        self.__mask = None

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
