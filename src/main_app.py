import tkinter
from tkinter import ttk
from typing import Set, Dict, Tuple, List
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np


class ForksGUI:
    """
    Main class for launch Forks GUI
    """
    def __init__(self, master: tkinter.Tk) -> None:
        self.master = master
        master.title("Fork feedthrough caclulation")
        self.label = tkinter.Label(master, text="This is our first GUI!")
        self.label.pack()

        self.greet_button = tkinter.Button(master, text="Greet_DIma", command=self.greet)
        self.greet_button.pack(side=tkinter.BOTTOM)

        self.close_button = tkinter.Button(master, text="Close", command=master.quit)
        self.close_button.pack(side=tkinter.BOTTOM)

    def greet(self) -> None:
        print("HIIIIIIIIIIII!!!!")

    def figure_1(self) -> None:
        """
        figure in matplotlib
        :return:
        """
        fig = Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
        canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


if __name__ == "__main__":
    root = tkinter.Tk()
    my_gui = ForksGUI(root)
    my_gui.figure_1()
    root.mainloop()