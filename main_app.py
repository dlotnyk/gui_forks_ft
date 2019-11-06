import tkinter
from tkinter import ttk
from typing import Set, Dict, Tuple, List


class ForksGUI:
    """
    Main class for launch Forks GUI
    """
    def __init__(self, master: tkinter.Tk) -> None:
        self.master = master
        master.title("Fork feedthrough caclulation")
        self.label = tkinter.Label(master, text="This is our first GUI!")
        self.label.pack()

        self.greet_button = tkinter.Button(master, text="Greet", command=self.greet)
        self.greet_button.pack()

        self.close_button = tkinter.Button(master, text="Close", command=master.quit)
        self.close_button.pack()

    def greet(self):
        print("HIIIIIIIIIIII!!!!")


if __name__ == "__main__":
    root = tkinter.Tk()
    my_gui = ForksGUI(root)
    root.mainloop()