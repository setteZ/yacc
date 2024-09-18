"""
Yet another CANopen configurator
"""

import argparse
import logging
import platform
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
from __init__ import __version__ as VERSION

# dependancies
from tqdm import tqdm


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["upload", "download", "save"], nargs="?")
    parser.add_argument("-f", "--file", default="")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--info", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.info:
        logging.basicConfig(level=logging.INFO)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.disable(logging.CRITICAL)

    eds_file = []
    current_dir = os.getcwd()
    for x in os.listdir(current_dir):
        if x.endswith(".EDS"):
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
                eds_file = [toml_dict["object_dictionary"]["filename"]]
                ITF = toml_dict["can"]["interface"]
                BAUD = int(toml_dict["can"]["baudrate"])
                NID = int(toml_dict["can"]["nodeid"])
                logging.info("%s | %s | %s | %s", eds_file, ITF, BAUD, NID)
    else:
        ITF = "peak"
        BAUD = 250
        NID = 1
        logging.info("missing config.toml file")

    if len(eds_file) == 1:
        EDS = os.path.join(current_dir, eds_file[0])
    else:
        EDS = ""
    if args.file == "":
        args.file = EDS

    device = Device(filename=args.file, baudrate=BAUD, nodeid=NID, interface=ITF)
    if args.command == "upload":
        if not os.path.isfile(args.file):
            print(f"{args.file} does not exist")
            sys.exit(1)
        try:
            device.connect()
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.debug(err)
            print("I can't connect to the device")
            sys.exit(1)

        print("uploading from the device...")
        iteration = device.get_objdict_elements(args.file)
        try:
            with tqdm(total=iteration) as pbar:
                for _ in device.upload_dcf(True):
                    pbar.update(1)
        except Exception as err:  # pylint: disable=broad-exception-caught
            print(f"error: {err}")
            sys.exit(1)
        else:
            sys.exit(0)
        finally:
            device.disconnect()

    if args.command == "download":
        if not os.path.isfile(args.file):
            print(f"{args.file} does not exist")
            sys.exit(1)
        try:
            device.connect()
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.debug(err)
            print("I can't connect to the device")
            sys.exit(1)

        print("downloading to the device...")
        iteration = device.get_objdict_elements(args.file)
        try:
            with tqdm(total=iteration) as pbar:
                for _ in device.download_dcf(args.file, True):
                    pbar.update(1)
        except Exception as err:  # pylint: disable=broad-exception-caught
            print(f"error: {err}")
            sys.exit(1)
        else:
            if args.save:
                device.save()
                print("saved")
            else:
                print("remember to save (if needed)")
            sys.exit(0)
        finally:
            device.disconnect()

    if args.command == "save":
        try:
            device.connect()
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.debug(err)
            print("I can't connect to the device")
            sys.exit(1)

        print("saving")
        try:
            device.save()
        except Exception as err:  # pylint: disable=broad-exception-caught
            print(err)
            sys.exit(1)
        else:
            print("done")
            sys.exit(0)
        finally:
            device.disconnect()

    if args.command is None:
        window = tk.Tk()
        root_path = os.path.dirname(__file__)
        if not (getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")):
            root_path = root_path[:-4]
        icon_path = os.path.join(root_path, "media", "y.ico")
        if platform.system() == "Linux":
            icon_path = None
        Gui(
            window,
            device,
            interface=ITF,
            baudrate=BAUD,
            nodeid=NID,
            eds_file=args.file,
            version=VERSION,
            icon=icon_path,
        )
        window.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        LOGFILE = "yacc.log"
        with open(LOGFILE, mode="a", encoding="utf-8") as fp:
            fp.write(f"{err}")
        print(f"A {LOGFILE} file has been generated for an unexpected error.")
        print("Please report it to https://github.com/setteZ/yacc")
