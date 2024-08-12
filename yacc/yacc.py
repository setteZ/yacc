"""
Yet another CANopen configurator
"""

import argparse
import logging
import os
import sys
import tkinter as tk

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("error: missing both tomllib and tomli module")
        sys.exit(1)

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

    eds_file = []
    current_dir = os.getcwd()
    for x in os.listdir(current_dir):
        if x.endswith(".eds"):
            eds_file.append(x)
    toml_path = os.path.join(os.getcwd(), "config.toml")
    logging.info(toml_path)
    if os.path.exists(toml_path):
        with open(toml_path, "rb") as f:
            try:
                toml_dict = tomllib.load(f)
            except tomllib.TOMLDecodeError:
                logging.info("not a valid TOML file")
            else:
                eds_file = [toml_dict["file"]["filename"]]
                itf = toml_dict["can"]["interface"]
                baud = str(toml_dict["can"]["baudrate"])
                nid = str(toml_dict["can"]["nodeid"])
                logging.info("%s | %s | %s | %s", eds_file, itf, baud, nid)
    else:
        itf = "peak"
        baud = 250
        nid = 1
        logging.info("missing config.toml file")

    if len(eds_file) == 1:
        eds = os.path.join(current_dir, eds_file[0])
    if args.file == "":
        args.file = eds

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
        Gui(window, interface=itf, baudrate=baud, nodeid=nid, eds_file=args.file)
        window.mainloop()
