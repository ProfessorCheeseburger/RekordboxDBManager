import sys
import os
from tkinter import Tk
from dj_tagtool.gui import MusicTagsApp

def main():
    root = Tk()
    app = MusicTagsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
