"""
Module for device interaction
"""

import dataclasses
import logging
import struct

# requirements
import canopen

VERSION = "0.1.0-b"
ALPHA = ""
BETA = ""

if ALPHA != "" and BETA != "":
    import sys

    sys.exit(1)


@dataclasses.dataclass
class Data:
    """
    class to have different rappresentation of the data
    """

    signed: int = 0
    unsigned: int = 0
    hex: str = "0"
    float: float = 0.0
    bytes: bytes = b"\x00"
    length: int = 1


class Device:
    """
    class to define the device
    """

    def __init__(
        self,
        filename: str | None = None,
        baudrate: int = 250,
        nodeid: int = 1,
        interface: str = "peak",
    ):

        self.__version = VERSION
        if ALPHA != "":
            self.__version += "-alpha." + ALPHA
        if BETA != "":
            self.__version += "-beta." + BETA
        self.__filename = filename
        self.__baudrate = baudrate
        self.__nodeid = nodeid
        if interface not in ["peak", "kvaser", "ixxat"]:
            raise Exception("interface not available")
        if interface == "peak":
            self.__interface = "pcan"
            self.__channel = "PCAN_USBBUS1"
        else:
            self.__interface = interface
            self.__channel = 0
        self.__network = None
        self.__node = None

    def get_version(self):
        """
        method to ghet access to version
        """
        return self.__version

    def connect(self):
        """
        connecting function
        """
        try:
            self.__network = canopen.Network()
            self.__network.connect(
                channel=self.__channel,
                interface=self.__interface,
                bitrate=self.__baudrate * 1000,
            )
        except Exception as err:
            logging.debug(err)
        else:
            self.__node = self.__network.add_node(
                node=self.__nodeid, object_dictionary=self.__filename
            )
            self.__node.sdo.RESPONSE_TIMEOUT = 1

    def disconnect(self):
        """
        disconnect the network
        """
        self.__network.disconnect()

    def read_entry(self, index: int, subindex: int) -> Data:
        """
        read entry method
        """
        data = Data()
        try:
            data.bytes = self.__node.sdo.upload(index=index, subindex=subindex)
        except Exception as err:
            logging.debug(err)
            raise err
        else:
            ba = bytearray(data.bytes)
            ba.reverse()
            data.hex = "".join(f"{x:02X}" for x in ba)
            data.signed = int.from_bytes(bytes=data.bytes, byteorder="little")
            data.float = struct.unpack("!f", ba)[0]
            data.length = len(data.bytes)
            return data

    def write_entry(self):
        """
        write entry method
        """


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    device = Device()
    device.connect()
