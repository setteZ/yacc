"""
Yet another CANopen configurator
"""

import argparse
import logging
import os
import sys
import tkinter as tk

# local module
from gui import Gui

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["upload", "download"], nargs="?")
    parser.add_argument("-f", "--file", default="")
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--info", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.info:
        logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.command == "upload":
        if not os.path.isfile(args.file):
            print(f"{args.file} does not exist")
            sys.exit(1)
        print("upload action")
        sys.exit(0)

    if args.command == "download":
        if not os.path.isfile(args.file):
            print(f"{args.file} does not exist")
            sys.exit(1)
        print("download action")
        sys.exit(0)

    if args.command is None:
        window = tk.Tk()
        Gui(window)
        window.mainloop()
