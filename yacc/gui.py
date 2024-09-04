"""
Module for Graphical User Interface
"""

import logging
import os
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import struct


# requirements
from canopen.objectdictionary import datatypes
import tomli_w

# local module
from device import Device


class Gui(tk.Frame):
    """
    window creation for CAN configuration
    """

    def __init__(
        self,
        parent,
        device,
        interface="peak",
        baudrate=250,
        nodeid=1,
        eds_file="",
        version="",
        icon="",
    ):
        tk.Frame.__init__(self, parent)
        self.__version = version
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.__exit)
        self.variable_ele = None
        self.variable_grp = None
        self.idx_text = None
        self.sub_text = None
        self.file_str_entry = None
        self.eds_file = eds_file
        self.interface = interface
        self.baudrate = baudrate
        self.nodeid = nodeid
        self.variable_node = None
        self.device = device
        self.value_unsigned_text = None
        self.value_signed_text = None
        self.value_hex_text = None
        self.value_float_text = None
        self.length_text = None
        self.element_opt = None
        self.group_opt = None
        self.value_unsigned_entry = None
        self.value_signed_entry = None
        self.value_float_entry = None
        self.value_hex_entry = None
        self.save_button = None

        self.icon = icon

        self.parent.iconbitmap(icon)
        self.parent.title("")
        self.parent.resizable(False, False)
        self.__populate_parent()
        self.parent.withdraw()
        self.config_window = tk.Tk()
        self.config_window.iconbitmap(icon)
        self.config_window.protocol("WM_DELETE_WINDOW", self.__exit)
        self.__create_config_window()

    def __callback_itf(self, *args):
        """
        callback for interface selection
        """
        interface = self.interface_variable.get()
        logging.info(interface)

    def __callback_br(self, *args):
        """
        callback for baudrate selection
        """
        baudrate = self.variable_br.get()
        logging.info(baudrate)

    def __select_file(self):
        filetypes = (("eds files", "*.eds"), ("All files", "*.*"))

        filename = fd.askopenfilename(
            title="Open a file", initialdir=os.getcwd(), filetypes=filetypes
        )
        filename = os.path.abspath(filename)
        logging.info("selected file: %s", filename)
        self.file_str_entry.set(filename)

    def __create_config_window(self):
        """
        function to create the config window
        """

        self.config_window.title("configuration")
        self.config_window.resizable(False, False)

        file_frame = tk.LabelFrame(self.config_window, text="object dictionary")
        file_frame.grid(column=0, row=0)

        self.file_str_entry = tk.StringVar(file_frame)
        self.file_str_entry.set(self.eds_file)

        file_entry = tk.Entry(file_frame, textvariable=self.file_str_entry)
        file_entry.grid(column=0, row=0)
        file_button = tk.Button(
            file_frame, text="select file", command=self.__select_file
        )
        file_button.grid(column=1, row=0)

        interface_frame = tk.LabelFrame(self.config_window, text="interface")
        interface_frame.grid(column=0, row=1)
        interface_list = ["peak", "kvaser", "ixxat"]
        self.interface_variable = tk.StringVar(interface_frame)
        self.interface_variable.set(self.interface)
        interface_opt = tk.OptionMenu(
            interface_frame, self.interface_variable, *interface_list
        )
        interface_opt.pack()

        self.interface_variable.trace("w", self.__callback_itf)

        baudrate_frame = tk.LabelFrame(self.config_window, text="baudrate")
        baudrate_frame.grid(column=0, row=2)
        baudrate_list = ["125", "250", "500"]
        self.variable_br = tk.StringVar(baudrate_frame)
        self.variable_br.set(self.baudrate)
        baudrate_opt = tk.OptionMenu(baudrate_frame, self.variable_br, *baudrate_list)
        baudrate_opt.pack()

        self.variable_br.trace("w", self.__callback_br)

        nodeid_frame = tk.LabelFrame(self.config_window, text="node id")
        nodeid_frame.grid(column=0, row=3)
        self.variable_node = tk.StringVar(nodeid_frame, value=self.nodeid)
        nodeid_entry = tk.Entry(nodeid_frame, textvariable=self.variable_node)
        nodeid_entry.pack()

        button_frame = tk.Frame(self.config_window)
        button_frame.grid(column=0, row=4)
        connect_button = tk.Button(button_frame, text="connect", command=self.__connect)
        connect_button.grid(column=0, row=0)

    def __exit(self):
        self.config_window.destroy()
        self.parent.destroy()

    def __callback_ele(self, *args):
        """
        callback for element selection
        """
        element = self.variable_ele.get()
        if element != "":
            self.sub_text.set(self.device.get_sub(self.variable_grp.get(), element))

    def __callback_grp(self, *args):
        """
        callback for group selection
        """
        group = self.variable_grp.get()
        if group != "":
            sub = self.device.get_subidx_names(group)
            logging.info(sub)
            menu = self.element_opt["menu"]
            menu.delete(0, "end")
            if not sub:
                self.sub_text.set("0")
            else:
                for string in sub:
                    menu.add_command(
                        label=string,
                        command=lambda value=string: self.variable_ele.set(value),
                    )
                    self.element_opt.option_clear()
                self.sub_text.set("")

            idx = self.device.idx_from_name(self.variable_grp.get())
            self.idx_text.set(idx)
            self.variable_ele.set("")

    def __idx_enter(self, *args):
        """
        index enter reaction
        """
        self.variable_grp.set(
            self.device.get_group_from_idx(int(self.idx_text.get(), 16))
        )

    def __idx_typing(self, *args):
        """
        index typing reaction
        """
        logging.info("entry: idx %s sub %s", self.idx_text.get(), self.sub_text.get())
        self.variable_grp.set("")
        menu = self.element_opt["menu"]
        menu.delete(0, "end")
        self.variable_ele.set("")

    def __sub_typing(self, *args):
        """
        subindex typing reaction
        """
        logging.info("entry: idx %s sub %s", self.idx_text.get(), self.sub_text.get())
        self.variable_ele.set("")

    def __read_action(self):
        try:
            data = self.device.read_entry(
                index=int(self.idx_text.get(), 16),
                subindex=int(self.sub_text.get(), 16),
            )
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.debug(err)
            tk.messagebox.showerror("read", "error while reading")
        else:
            self.value_unsigned_text.set(str(data.unsigned))
            self.value_signed_text.set(str(data.signed))
            self.value_hex_text.set(data.hex)
            if data.length == 4:
                self.value_float_text.set(str(data.float))
            else:
                self.value_float_text.set("-")
            self.length_text.set(str(data.length))
            data_type = self.device.get_datatype(
                self.variable_grp.get(), self.variable_ele.get()
            )
            if data_type in datatypes.UNSIGNED_TYPES:
                self.value_unsigned_entry.config(fg="black")
                self.value_signed_entry.config(fg="grey")
                self.value_float_entry.config(fg="grey")
                self.value_hex_entry.config(fg="grey")
            elif data_type in datatypes.SIGNED_TYPES:
                self.value_unsigned_entry.config(fg="grey")
                self.value_signed_entry.config(fg="black")
                self.value_float_entry.config(fg="grey")
                self.value_hex_entry.config(fg="grey")
            elif data_type in datatypes.FLOAT_TYPES:
                self.value_unsigned_entry.config(fg="grey")
                self.value_signed_entry.config(fg="grey")
                self.value_float_entry.config(fg="black")
                self.value_hex_entry.config(fg="grey")
            else:
                logging.info(data_type)
                self.value_unsigned_entry.config(fg="grey")
                self.value_signed_entry.config(fg="grey")
                self.value_float_entry.config(fg="grey")
                self.value_hex_entry.config(fg="black")

    def __save_action(self):
        logging.info("save action")
        try:
            self.device.save()
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.debug(err)
            tk.messagebox.showerror("save", "error while saving")
        self.save_button.grid_forget()

    def __write_action(self):
        logging.info("write action")
        try:
            data = int(self.value_hex_text.get(), 16).to_bytes(
                int(self.length_text.get()), "little"
            )
            self.device.write_entry(
                index=int(self.idx_text.get(), 16),
                subindex=int(self.sub_text.get(), 16),
                data=data,
            )
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.debug(err)
            tk.messagebox.showerror("write", "error while writing")
        else:
            self.value_unsigned_text.set("")
            self.value_signed_text.set("")
            self.value_float_text.set("")
            self.value_hex_text.set("")
            self.save_button.grid()

    def __connect(self):
        """
        new window creation after "connect" button is clicked
        """
        try:
            self.device.set_objdict(self.file_str_entry.get())
            self.device.set_baudrate(int(self.variable_br.get()))
            self.device.set_nodeid(int(self.variable_node.get()))
            self.device.set_interface(self.interface_variable.get())
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.debug(err)
            tk.messagebox.showerror(
                "connect", "there something wrong with the configuration"
            )
        else:
            try:
                self.device.connect()
            except Exception as err:  # pylint: disable=broad-exception-caught
                logging.debug(err)
                tk.messagebox.showerror("connect", "I can't connect to the device")
            else:
                config = {
                    "object_dictionary": {
                        "filename": self.file_str_entry.get()
                    },
                    "can": {
                        "interface": self.interface_variable.get(),
                        "baudrate": int(self.variable_br.get()),
                        "nodeid": int(self.variable_node.get()),
                    },
                }
                with open("config.toml", "wb") as f:
                    tomli_w.dump(config, f)
                logging.info(
                    "interface = %s | baudrate = %s | node-id = %s | eds = %s",
                    self.interface_variable.get(),
                    self.variable_br.get(),
                    self.variable_node.get(),
                    self.file_str_entry.get(),
                )

                self.config_window.withdraw()
                self.parent.deiconify()

                if os.path.exists(self.file_str_entry.get()):
                    group_list = self.device.get_group_name_list()
                    logging.debug(group_list)
                    self.variable_ele.set("")
                    menu = self.group_opt["menu"]
                    menu.delete(0, "end")
                    for string in group_list:
                        menu.add_command(
                            label=string,
                            command=lambda value=string: self.variable_grp.set(value),
                        )
                else:
                    logging.info("no file")

    def __license(self):
        message = "Copyright 2024 setteZ\nSPDX-License-Identifier: Apache-2.0"
        tk.messagebox.showinfo("License", message)

    def __info(self):
        message = f"version: {self.__version}"
        tk.messagebox.showinfo("info", message)

    def __upload_dcf(self):
        wait_msg = tk.Tk()
        wait_msg.title("")
        wait_msg.iconbitmap(self.icon)
        wait_label = tk.Label(wait_msg, text="Uploading...")
        wait_label.grid(column=0, row=0)
        iteration = self.device.get_objdict_elements(None)
        pb = ttk.Progressbar(wait_msg, orient=tk.HORIZONTAL, length=iteration, mode="determinate")
        pb.grid(column=0, row=1)
        try:
            for _ in self.device.upload_dcf(True):
                wait_msg.update_idletasks()
                pb['value'] += 1
                pb.update()
            self.device.upload_dcf()
        except Exception as err:  # pylint: disable=broad-exception-caught
            tk.messagebox.showerror("dcf upload", err)
        else:
            tk.messagebox.showinfo("dcf upload", "done")
        finally:
            wait_msg.destroy()

    def __download_dcf(self):

        filetypes = (("dcf files", "*.dcf"), ("All files", "*.*"))

        filename = fd.askopenfilename(
            title="Select .dcf file", initialdir=os.getcwd(), filetypes=filetypes
        )
        wait_msg = tk.Tk()
        wait_msg.title("")
        wait_msg.iconbitmap(self.icon)
        wait_label = tk.Label(wait_msg, text="Downloading...")
        wait_label.grid(column=0, row=0)
        iteration = self.device.get_objdict_elements(filename)
        pb = ttk.Progressbar(wait_msg, orient=tk.HORIZONTAL, length=iteration, mode="determinate")
        pb.grid(column=0, row=1)
        try:
            for _ in self.device.download_dcf(filename, True):
                wait_msg.update_idletasks()
                pb['value'] += 1
                pb.update()
        except Exception as err:  # pylint: disable=broad-exception-caught
            tk.messagebox.showerror("dcf download", err)
        else:
            answer = tk.messagebox.askquestion(
                "dcf download", "done, do you wanna save?"
            )
            if answer == tk.messagebox.YES:
                self.device.save()
        finally:
            wait_msg.destroy()

    def __populate_parent(self):
        """
        function to populate the main app window
        """

        self.parent.title(f"YACC - {self.__version}")
        # menu bar
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=False)

        file_menu.add_command(
            label="Exit",
            command=self.__exit,
        )
        menubar.add_cascade(label="File", menu=file_menu, underline=0)

        config_menu = tk.Menu(menubar, tearoff=False)
        config_menu.add_command(
            label="Upload dcf (read)",
            command=self.__upload_dcf,
        )

        config_menu.add_command(
            label="Download dcf (write)",
            command=self.__download_dcf,
        )
        menubar.add_cascade(label="Configuration", menu=config_menu, underline=0)

        help_menu = tk.Menu(menubar, tearoff=False)

        help_menu.add_command(
            label="License",
            command=self.__license,
        )

        help_menu.add_command(
            label="About",
            command=self.__info,
        )
        menubar.add_cascade(label="Help", menu=help_menu, underline=0)

        # entry frame
        entry_frame = tk.Frame(self.parent)
        entry_frame.grid(column=0, row=0)
        ## element
        element_frame = tk.LabelFrame(entry_frame, text="element")
        element_frame.grid(column=1, row=0)
        self.variable_ele = tk.StringVar(element_frame)
        self.variable_ele.set("")
        self.element_opt = tk.OptionMenu(element_frame, self.variable_ele, *[""])
        self.element_opt.pack()

        self.variable_ele.trace("w", self.__callback_ele)

        ## group
        group_frame = tk.LabelFrame(entry_frame, text="group")
        group_frame.grid(column=0, row=0)
        self.variable_grp = tk.StringVar(group_frame)
        self.variable_grp.set("")
        self.group_opt = tk.OptionMenu(group_frame, self.variable_grp, *[""])
        self.group_opt.pack()

        self.variable_grp.trace("w", self.__callback_grp)

        ## idx
        idx_frame = tk.LabelFrame(entry_frame, text="index [0x]")
        idx_frame.grid(column=0, row=1)
        self.idx_text = tk.StringVar(idx_frame)
        idx_entry = tk.Entry(idx_frame, textvariable=self.idx_text)

        idx_entry.bind("<Key>", self.__idx_typing)
        idx_entry.bind("<Return>", self.__idx_enter)
        idx_entry.pack()

        ## sub
        self.sub_text = tk.StringVar()
        sub_frame = tk.LabelFrame(entry_frame, text="subindex [0x]")
        sub_frame.grid(column=1, row=1)
        sub_entry = tk.Entry(sub_frame, textvariable=self.sub_text)

        sub_entry.bind("<Key>", self.__sub_typing)
        sub_entry.pack()

        # command frame
        command_frame = tk.Frame(self.parent)
        command_frame.grid(column=1, row=0)

        ## read

        read_button = tk.Button(command_frame, text="read", command=self.__read_action)
        read_button.grid(column=0, row=0)

        ## write

        write_button = tk.Button(
            command_frame, text="write", command=self.__write_action
        )
        write_button.grid(column=0, row=1)

        ## save

        self.save_button = tk.Button(
            command_frame, text="save", command=self.__save_action
        )
        self.save_button.grid(column=0, row=2)
        self.save_button.grid_forget()

        # data frame
        data_frame = tk.Frame(self.parent)
        data_frame.grid(column=2, row=0)

        ## length
        self.length_text = tk.StringVar()
        length_frame = tk.LabelFrame(data_frame, text="length")
        length_frame.grid(column=0, row=0)
        length_entry = tk.Entry(length_frame, textvariable=self.length_text)

        length_entry.pack()

        ## value
        value_frame = tk.LabelFrame(data_frame, text="value")
        value_frame.grid(column=0, row=1)

        value_unsigned_label = tk.Label(value_frame, text="unsigned")
        value_unsigned_label.grid(column=0, row=0)
        self.value_unsigned_text = tk.StringVar()
        self.value_unsigned_entry = tk.Entry(
            value_frame, textvariable=self.value_unsigned_text
        )
        self.value_unsigned_entry.grid(column=1, row=0)
        self.value_unsigned_entry.bind("<Return>", self.__unsigned_typing)

        value_signed_label = tk.Label(value_frame, text="signed")
        value_signed_label.grid(column=0, row=1)
        self.value_signed_text = tk.StringVar()
        self.value_signed_entry = tk.Entry(
            value_frame, textvariable=self.value_signed_text
        )
        self.value_signed_entry.grid(column=1, row=1)
        self.value_signed_entry.bind("<Return>", self.__signed_typing)

        value_float_label = tk.Label(value_frame, text="float")
        value_float_label.grid(column=0, row=2)
        self.value_float_text = tk.StringVar()
        self.value_float_entry = tk.Entry(
            value_frame, textvariable=self.value_float_text
        )
        self.value_float_entry.grid(column=1, row=2)
        self.value_float_entry.bind("<Return>", self.__float_typing)

        value_hex_label = tk.Label(value_frame, text="hex")
        value_hex_label.grid(column=0, row=3)
        self.value_hex_text = tk.StringVar()
        self.value_hex_entry = tk.Entry(value_frame, textvariable=self.value_hex_text)
        self.value_hex_entry.grid(column=1, row=3)
        self.value_hex_entry.bind("<Return>", self.__hex_typing)

        # main button frame

        new_button_frame = tk.Frame(self.parent)
        new_button_frame.grid(column=0, row=4)
        new_connect_button = tk.Button(
            new_button_frame, text="disconnect", command=self.__disconnect
        )
        new_connect_button.grid(column=0, row=0)

    def __disconnect(self):
        logging.info("disconnect reaction")

        self.device.disconnect()
        self.parent.withdraw()
        self.config_window.deiconify()

    def __unsigned_typing(self, *args):
        """
        function to convert from unsigned
        """
        logging.info("unsigned entered")
        try:
            data_length = int(self.length_text.get())
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.debug(err)
            tk.messagebox.showerror("data", "wrong lenght")
        else:
            try:
                data_unsigned = int(self.value_unsigned_entry.get(), 10)
            except Exception as err:  # pylint: disable=broad-exception-caught
                logging.debug(err)
                tk.messagebox.showerror("data", "wrong unsigned value")
            else:
                data_hex = f"{data_unsigned:0{data_length*2}x}"
                self.value_hex_text.set(data_hex)
                self.value_signed_text.set("-")
                self.value_float_text.set("-")
        self.value_unsigned_entry.config(fg="black")
        self.value_signed_entry.config(fg="black")
        self.value_float_entry.config(fg="black")
        self.value_hex_entry.config(fg="black")

    def __signed_typing(self, *args):
        """
        function to convert from signed
        """
        logging.info("signed entered")
        self.value_unsigned_text.set("-")
        self.value_signed_text.set("-")
        self.value_float_text.set("-")
        self.value_hex_text.set("-")
        self.value_unsigned_entry.config(fg="black")
        self.value_signed_entry.config(fg="black")
        self.value_float_entry.config(fg="black")
        self.value_hex_entry.config(fg="black")
        tk.messagebox.showinfo("data", "signed conversion not yet implemented")

    def __float_typing(self, *args):
        """
        function to convert from float
        """
        logging.info("float entered")
        try:
            data_float = float(self.value_float_text.get())
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.debug(err)
            tk.messagebox.showerror("data", "wrong float")
        else:
            data_bytes = struct.pack(">f", data_float)
            self.value_hex_text.set(data_bytes.hex())
            self.value_unsigned_text.set("-")
            self.value_signed_text.set("-")
            self.length_text.set(4)
        self.value_unsigned_entry.config(fg="black")
        self.value_signed_entry.config(fg="black")
        self.value_float_entry.config(fg="black")
        self.value_hex_entry.config(fg="black")

    def __hex_typing(self, *args):
        """
        function to convert from hex
        """
        logging.info("hex entered")
        data_hex = self.value_hex_text.get()
        if len(data_hex) % 2:
            data_hex = f"0{data_hex}"
            self.value_hex_text.set(data_hex)
        data_bytes = bytes.fromhex(data_hex)
        data_length = len(data_bytes)
        ba = bytearray(data_bytes)
        "a".encode()
        ba.reverse()
        data_unsigned = int.from_bytes(bytes=data_bytes, byteorder="little")
        self.value_unsigned_text.set(data_unsigned)
        if data_length == 4:
            self.value_float_text.set(struct.unpack("<f", ba)[0])
        self.length_text.set(str(data_length))
        self.value_unsigned_entry.config(fg="black")
        self.value_signed_entry.config(fg="black")
        self.value_float_entry.config(fg="black")
        self.value_hex_entry.config(fg="black")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    window = tk.Tk()
    dev = Device()
    Gui(window, dev)
    window.mainloop()
