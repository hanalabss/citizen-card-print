import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import tkinter as tk
from src.app import VisitorCardApp

def main():
    root = tk.Tk()
    app = VisitorCardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()