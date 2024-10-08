"""
Module for device interaction
"""

import dataclasses
import logging
import struct
import time

# requirements
import canopen


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

        if filename == "":
            self.__filename = None
        else:
            self.__filename = filename
        self.__baudrate = baudrate
        self.__nodeid = nodeid
        if interface not in ["peak", "kvaser", "ixxat"]:
            raise Exception(  # pylint: disable=broad-exception-raised
                "interface not available"
            )
        self.set_interface(interface)
        self.__network = None
        self.__node = None

    def __pdo_enable(self, index):
        """
        method to enable the PDO, and return the previous state of the pdo
        """
        major = index & 0xFF00
        minor = index & 0x00FF
        if major in [0x1400, 0x1600]:
            transmission_idx = 0x1400
        elif major in [0x1800, 0x1A00]:
            transmission_idx = 0x1800
        transmission_idx += minor
        self.__node.nmt.state = "PRE-OPERATIONAL"
        self.__node.nmt.wait_for_heartbeat()
        assert self.__node.nmt.state == "PRE-OPERATIONAL"
        cobid = self.__node.sdo.upload(transmission_idx, 0x01)
        cobid_int = int(cobid.hex(), 16)
        if cobid_int & 0x80:
            cobid_enabled = (int(cobid.hex(), 16) & 0xFFFFFF7F).to_bytes(4, "big")
            cobid = self.__node.sdo.download(transmission_idx, 0x01, cobid_enabled)
            return False
        return True

    def __pdo_disable(self, index):
        """
        method to disable the PDO, and return the previous state of the pdo
        """
        major = index & 0xFF00
        minor = index & 0x00FF
        if major in [0x1400, 0x1600]:
            transmission_idx = 0x1400
        elif major in [0x1800, 0x1A00]:
            transmission_idx = 0x1800
        transmission_idx += minor
        self.__node.nmt.state = "PRE-OPERATIONAL"
        self.__node.nmt.wait_for_heartbeat()
        assert self.__node.nmt.state == "PRE-OPERATIONAL"
        cobid = self.__node.sdo.upload(transmission_idx, 0x01)
        cobid_int = int(cobid.hex(), 16)
        if not cobid_int & 0x80:
            cobid_disabled = (int(cobid.hex(), 16) | 0x80).to_bytes(4, "big")
            cobid = self.__node.sdo.download(transmission_idx, 0x01, cobid_disabled)
            return True
        return False

    def __pdo_mapping_disable(self, index):
        """
        method to disable the PDO, and return the previous state of the pdo
        """
        major = index & 0xFF00
        minor = index & 0x00FF
        transmission_idx = major + minor
        self.__node.nmt.state = "PRE-OPERATIONAL"
        self.__node.nmt.wait_for_heartbeat()
        assert self.__node.nmt.state == "PRE-OPERATIONAL"
        mapped_elements = self.__node.sdo.upload(transmission_idx, 0x00)
        mapped_elements_int = int(mapped_elements.hex(), 16)
        if mapped_elements_int:
            cobid = self.__node.sdo.download(transmission_idx, 0x00, b"\x00")
            return True
        return False

    def set_objdict(self, objdict):
        """
        method to set the object dictionary aka eds file
        """
        if objdict == "":
            objdict = None
        self.__filename = objdict

    def set_baudrate(self, baudrate):
        """
        method to set the baudrate
        """
        self.__baudrate = baudrate

    def set_nodeid(self, nodeid):
        """
        method to set the nodeid
        """
        self.__nodeid = nodeid

    def set_interface(self, interface):
        """
        method to set the interface
        """
        if interface == "peak":
            self.__interface = "pcan"
            self.__channel = "PCAN_USBBUS1"
        else:
            self.__interface = interface
            self.__channel = 0

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
            raise err
        self.__node = self.__network.add_node(
            node=self.__nodeid, object_dictionary=self.__filename
        )
        self.__node.object_dictionary.node_id = self.__nodeid
        self.__node.object_dictionary.bitrate = self.__baudrate * 1000
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
        logging.info("index = %d, subindex = %d", index, subindex)
        data = Data()
        try:
            data.bytes = self.__node.sdo.upload(index=index, subindex=subindex)
        except Exception as err:
            logging.debug(err)
            raise err
        data.length = len(data.bytes)
        ba = bytearray(data.bytes)
        ba.reverse()
        data.hex = "".join(f"{x:02X}" for x in ba)
        data.unsigned = int.from_bytes(bytes=data.bytes, byteorder="little")
        data.signed = int.from_bytes(bytes=data.bytes, byteorder="little", signed=True)
        if data.length == 4:
            data.float = struct.unpack("!f", ba)[0]
        return data

    def write_entry(self, index: int, subindex: int, data: bytes):
        """
        write entry method
        """
        try:
            self.__node.sdo.download(index, subindex, data)
        except Exception as err:
            raise err

    def get_group_from_idx(self, idx: int) -> str:
        """
        get the group name from the index ref
        """
        group = ""
        try:
            name = self.__node.object_dictionary[idx].name
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.debug(err)
        else:
            group = name
        return group

    def get_group_name_list(self):
        """
        get the list of the index name of the object dictionary
        """
        names = []
        self.__node.object_dictionary.values()
        for obj in self.__node.object_dictionary.values():
            names.append(obj.name)
        return names

    def get_subidx_names(self, idx_name: str):
        """
        get the list of the subindex name of the object dictionary
        """
        names = []
        obj = self.__node.object_dictionary[idx_name]
        logging.info("%s %s", idx_name, obj)
        if isinstance(obj, canopen.objectdictionary.ODRecord):
            for subobj in obj.values():
                names.append(subobj.name)
        return names

    def idx_from_name(self, name: str) -> str:
        """
        get index from name reference
        """
        obj = self.__node.object_dictionary[name]
        return f"{obj.index:X}"

    def get_sub(self, group_name: str, entry_name: str) -> str:
        """
        get the subindex of an entry given the name
        """
        obj = self.__node.object_dictionary[group_name][entry_name]
        return f"{obj.subindex:X}"

    def get_datatype(self, group_name: str, entry_name: str) -> str:
        """
        get the datatype of an entry given the name
        """
        obj = self.__node.object_dictionary[group_name]
        if isinstance(obj, canopen.objectdictionary.ODRecord):
            obj = obj[entry_name]
        return obj.data_type

    def download_dcf(self, filename: str, generate_iterator=False):
        """
        function to download a dcf file
        """
        od = canopen.import_od(filename)
        for obj in od.values():
            idx = obj.index
            if isinstance(obj, canopen.objectdictionary.ODRecord):
                for subobj in obj.values():
                    subidx = subobj.subindex
                    if subobj.access_type == "rw":
                        pdo_was_enabled = False
                        mapping_was_enabled = False
                        if (idx & 0xFF00) in [0x1400, 0x1600, 0x1800, 0x1A00]:
                            pdo_was_enabled = self.__pdo_disable(idx)
                        if (idx & 0xFF00) in [0x1600, 0x1A00]:
                            mapping_was_enabled = self.__pdo_mapping_disable(idx)
                        value = od[idx][subidx].value
                        try:
                            raw = od[idx][subidx].encode_raw(value)
                        except Exception as err:
                            raise Exception(  # pylint: disable=broad-exception-raised
                                f"problem with the value of 0x{idx:04X} 0x{subidx:02X}: {err}"
                            ) from err
                        try:
                            self.__node.sdo.download(idx, subidx, raw)
                        except Exception as err:
                            message = f"problem writing {raw} to 0x{idx:04X} 0x{subidx:02X} {subobj.name}: {err}"
                            raise Exception(  # pylint: disable=broad-exception-raised
                                message
                            ) from err
                        if mapping_was_enabled:
                            try:
                                value = od[idx][0].value
                                raw = od[idx][0].encode_raw(value)
                            except Exception as err:
                                raise Exception(  # pylint: disable=broad-exception-raised
                                    f"problem with the value of 0x{idx:04X} 0x00 to ri-enable the PDO mapping: {err}"
                                ) from err
                            try:
                                self.__node.sdo.download(idx, 0, raw)
                            except Exception as err:
                                message = f"problem writing {raw} to 0x{idx:04X} 0x00 {subobj.name} to ri-enable the PDO mapping: {err}"
                                raise Exception(  # pylint: disable=broad-exception-raised
                                    message
                                ) from err
                        if pdo_was_enabled:
                            self.__pdo_enable(idx)
                    if generate_iterator:
                        yield

            if isinstance(obj, canopen.objectdictionary.ODVariable):
                subidx = obj.subindex
                if obj.access_type == "rw":
                    value = od[idx].value
                    try:
                        raw = od[idx].encode_raw(value)
                    except Exception as err:
                        raise Exception(  # pylint: disable=broad-exception-raised
                            f"problem with the value of 0x{idx:04X} 0x{subidx:02X}: {err}"
                        ) from err
                    try:
                        self.__node.sdo.download(idx, subidx, raw)
                    except Exception as err:
                        message = f"problem writing 0x{idx:04X} 0x{subidx:02X} {obj.name}: {err}"
                        raise Exception(  # pylint: disable=broad-exception-raised
                            message
                        ) from err
                if generate_iterator:
                    yield

    def get_objdict_elements(self, filename: str | None = None):
        """
        function to get the number of elemnts present in the obj file
        """
        number_of_elements = 0
        if filename:
            od = canopen.import_od(filename)
        else:
            od = self.__node.object_dictionary
        for obj in od.values():
            if isinstance(obj, canopen.objectdictionary.ODRecord):
                number_of_elements += len(obj.keys())

            if isinstance(obj, canopen.objectdictionary.ODVariable):
                number_of_elements += 1

        return number_of_elements

    def upload_dcf(self, generate_iterator=False):
        """
        function to upload a dcf file
        """
        for obj in self.__node.object_dictionary.values():
            logging.debug("0x%X %s", obj.index, obj.name)
            if isinstance(obj, canopen.objectdictionary.ODRecord):
                for subobj in obj.values():
                    try:
                        value = self.__node.sdo.upload(obj.index, subobj.subindex)
                    except Exception as err:
                        raise Exception(  # pylint: disable=broad-exception-raised
                            f"problem with 0x{obj.index:04X} 0x{subobj.subindex:02X}: {err}"
                        ) from err
                    value = self.__node.object_dictionary[obj.index][
                        subobj.subindex
                    ].decode_raw(value)
                    self.__node.object_dictionary[obj.index][
                        subobj.subindex
                    ].value_raw = value
                    if generate_iterator:
                        yield

            if isinstance(obj, canopen.objectdictionary.ODVariable):
                try:
                    value = self.__node.sdo.upload(obj.index, obj.subindex)
                except Exception as err:
                    raise Exception(  # pylint: disable=broad-exception-raised
                        f"problem with 0x{obj.index:04X} 0x{obj.subindex:02X}: {err}"
                    ) from err
                value = self.__node.object_dictionary[obj.index].decode_raw(value)
                self.__node.object_dictionary[obj.index].value_raw = value
                if generate_iterator:
                    yield

        canopen.objectdictionary.export_od(
            self.__node.object_dictionary,
            f"upload_{time.strftime('%y%m%d-%H%M%S', time.localtime())}.dcf",
            "dcf",
        )

    def save(self):
        """
        save request
        """
        self.__node.sdo.download(0x1010, 0x01, b"save")

    def default(self):
        """
        load default request
        """
        self.__node.sdo.download(0x1011, 0x01, b"load")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    device = Device()
    device.connect()
