"""
Module for device interaction
"""

import logging

# requirements
import canopen

VERSION = "0.1.0-b"
ALPHA = ""
BETA = ""

if ALPHA != "" and BETA != "":
    import sys

    sys.exit(1)


class Device:
    """
    class to define the device
    """

    def __init__(
        self,
        filename=None,
        baudrate=250,
        nodeid=1,
        interface="peak",
        channel="PCAN_USBBUS1",
        output=None,
    ):

        self.__version = VERSION
        if ALPHA != "":
            self.__version += "-alpha." + ALPHA
        if BETA != "":
            self.__version += "-beta." + BETA
        self.__filename = filename
        self.__baudrate = baudrate
        self.__nodeid = nodeid
        self.__interface = interface
        self.__channel = channel
        self.__output = output

    def get_version(self):
        """
        method to ghet access to version
        """
        return self.__version

    def connect(self):
        """
        connecting function
        """

    def read_entry(self):
        """
        read entry method
        """

    def write_entry(self):
        """
        write entry method
        """


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
