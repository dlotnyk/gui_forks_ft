import numpy as np
from typing import Set, Dict, Tuple, List, Optional
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
