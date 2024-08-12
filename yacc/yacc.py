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
from device import Device

VER = "0.1.0"
ALPHA = ""
BETA = "1"

if ALPHA != "" and BETA != "":
    sys.exit(1)

VERSION = VER
if ALPHA != "":
    VERSION += "-alpha." + ALPHA
if BETA != "":
    VERSION += "-beta." + BETA

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["upload", "download"], nargs="?")
    parser.add_argument("-f", "--file", default="")
    parser.add_argument("--version", action="version", version=VERSION)
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

    device = Device(filename=args.file, baudrate=baud, nodeid=nid, interface=itf)
    if args.command == "upload":
        if not os.path.isfile(args.file):
            print(f"{args.file} does not exist")
            sys.exit(1)
        try:
            device.connect()
        except Exception as err:
            logging.debug(err)
            print("I can't connect to the device")
            sys.exit(1)

        print("uploading from the device...")
        try:
            device.upload_dcf()
        except Exception as err:
            print(f"error: {err}")
            sys.exit(1)
        else:
            print("done")
            sys.exit(0)
        finally:
            device.disconnect()

    if args.command == "download":
        if not os.path.isfile(args.file):
            print(f"{args.file} does not exist")
            sys.exit(1)
        try:
            device.connect()
        except Exception as err:
            logging.debug(err)
            print("I can't connect to the device")
            sys.exit(1)

        print("downloading to the device...")
        try:
            device.download_dcf(args.file)
        except Exception as err:
            print(f"error: {err}")
            sys.exit(1)
        else:
            print("done")
            sys.exit(0)
        finally:
            device.disconnect()

    if args.command is None:
        window = tk.Tk()
        Gui(
            window,
            device,
            interface=itf,
            baudrate=baud,
            nodeid=nid,
            eds_file=args.file,
            version=VERSION,
        )
        window.mainloop()
