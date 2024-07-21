"""
Module for application
"""

import logging
import os
import tkinter as tk
from tkinter import filedialog as fd

# requirements
from canopen.objectdictionary import datatypes

# local module
from device import Device

VERSION = "0.1.0"
ALPHA = "1"
BETA = ""

if ALPHA != "" and BETA != "":
    import sys

    sys.exit(1)


class App(tk.Frame):
    """
    window creation for CAN configuration
    """

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.__version = VERSION
        if ALPHA != "":
            self.__version += "-alpha." + ALPHA
        if BETA != "":
            self.__version += "-beta." + BETA
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.__exit)
        self.variable_ele = None
        self.variable_grp = None
        self.idx_text = None
        self.sub_text = None
        self.file_str_entry = None
        self.variable_node = None
        self.device = None
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

        self.parent.title("")
        self.parent.resizable(False, False)
        self.__populate_parent()
        self.parent.withdraw()
        self.config_window = tk.Tk()
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
        logging.info("selected file: %s", filename)
        self.file_str_entry.set(filename)

    def __create_config_window(self):
        """
        function to create the config window
        """

        self.config_window.title("configuration")
        self.config_window.resizable(False, False)

        file_frame = tk.LabelFrame(self.config_window, text="file")
        file_frame.grid(column=0, row=0)

        self.file_str_entry = tk.StringVar(file_frame)

        eds_file = []
        current_dir = os.getcwd()
        for x in os.listdir(current_dir):
            if x.endswith(".eds"):
                eds_file.append(x)
        if len(eds_file) == 1:
            self.file_str_entry.set(os.path.join(current_dir,eds_file[0]))
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
        self.interface_variable.set(interface_list[0])
        interface_opt = tk.OptionMenu(
            interface_frame, self.interface_variable, *interface_list
        )
        interface_opt.pack()

        self.interface_variable.trace("w", self.__callback_itf)

        baudrate_frame = tk.LabelFrame(self.config_window, text="baudrate")
        baudrate_frame.grid(column=0, row=2)
        baudrate_list = ["125", "250", "500"]
        self.variable_br = tk.StringVar(baudrate_frame)
        self.variable_br.set(baudrate_list[1])
        baudrate_opt = tk.OptionMenu(baudrate_frame, self.variable_br, *baudrate_list)
        baudrate_opt.pack()

        self.variable_br.trace("w", self.__callback_br)

        nodeid_frame = tk.LabelFrame(self.config_window, text="node id")
        nodeid_frame.grid(column=0, row=3)
        self.variable_node = tk.StringVar(nodeid_frame, value="1")
        nodeid_entry = tk.Entry(nodeid_frame, textvariable=self.variable_node)
        nodeid_entry.pack()

        button_frame = tk.Frame(self.config_window)
        button_frame.grid(column=0, row=4)
        connect_button = tk.Button(button_frame, text="connect", command=self.__connect)
        exit_button = tk.Button(button_frame, text="exit", command=self.__exit)
        connect_button.grid(column=0, row=0)
        exit_button.grid(column=1, row=0)

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
        sub = self.device.get_subidx_names(group)
        logging.info(sub)
        menu = self.element_opt["menu"]
        menu.delete(0, "end")
        for string in sub:
            menu.add_command(
                label=string,
                command=lambda value=string: self.variable_ele.set(value),
            )
            self.element_opt.option_clear()

        if group != "":
            idx = self.device.idx_from_name(self.variable_grp.get())
            self.idx_text.set(idx)
            self.variable_ele.set("")
            self.sub_text.set("")

    def __entry_typing(self, *args):
        """
        entry_typing reaction
        """
        logging.info("entry: idx %s sub %s", self.idx_text.get(), self.sub_text.get())
        self.variable_grp.set("")
        self.variable_ele.set("")

    def __read_action(self):
        try:
            data = self.device.read_entry(
                index=int(self.idx_text.get(), 16),
                subindex=int(self.sub_text.get(), 16),
            )
        except Exception as err:
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
            data_type = self.device.get_datatype(self.variable_grp.get(), self.variable_ele.get())
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

    def __write_action(self):
        logging.info("write action")

    def __connect(self):
        """
        new window creation after "connect" button is clicked
        """
        try:
            self.device = Device(
                self.file_str_entry.get(),
                int(self.variable_br.get()),
                int(self.variable_node.get()),
                self.interface_variable.get(),
            )
        except Exception as err:
            logging.debug(err)
            tk.messagebox.showerror(
                "connect", "there something wrong with the configuration"
            )
        else:
            try:
                self.device.connect()
            except Exception as err:
                logging.debug(err)
                tk.messagebox.showerror("connect", "I can't connect to the device")
            else:
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

    def __info(self):
        message = f"app version: {self.__version}\ndevice version: {self.device.get_version()}"
        tk.messagebox.showinfo("info", message)

    def __populate_parent(self):
        """
        function to populate the main app window
        """

        # menu bar
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        help_menu = tk.Menu(menubar)

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
        element_list = [""]
        self.variable_ele = tk.StringVar(element_frame)
        self.variable_ele.set("")
        self.element_opt = tk.OptionMenu(
            element_frame, self.variable_ele, *element_list
        )
        self.element_opt.pack()

        self.variable_ele.trace("w", self.__callback_ele)

        ## group
        group_frame = tk.LabelFrame(entry_frame, text="group")
        group_frame.grid(column=0, row=0)
        group_list = ["group1", "group2", "group3"]
        self.variable_grp = tk.StringVar(group_frame)
        self.variable_grp.set("")
        self.group_opt = tk.OptionMenu(group_frame, self.variable_grp, *group_list)
        self.group_opt.pack()

        self.variable_grp.trace("w", self.__callback_grp)

        ## idx
        idx_frame = tk.LabelFrame(entry_frame, text="index [0x]")
        idx_frame.grid(column=0, row=1)
        self.idx_text = tk.StringVar(idx_frame)
        idx_entry = tk.Entry(idx_frame, textvariable=self.idx_text)

        idx_entry.bind("<Key>", self.__entry_typing)
        idx_entry.pack()

        ## sub
        self.sub_text = tk.StringVar()
        sub_frame = tk.LabelFrame(entry_frame, text="subindex [0x]")
        sub_frame.grid(column=1, row=1)
        sub_entry = tk.Entry(sub_frame, textvariable=self.sub_text)

        sub_entry.bind("<Key>", self.__entry_typing)
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
        write_button.grid_forget()

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

        value_signed_label = tk.Label(value_frame, text="signed")
        value_signed_label.grid(column=0, row=1)
        self.value_signed_text = tk.StringVar()
        self.value_signed_entry = tk.Entry(value_frame, textvariable=self.value_signed_text)
        self.value_signed_entry.grid(column=1, row=1)

        value_float_label = tk.Label(value_frame, text="float")
        value_float_label.grid(column=0, row=2)
        self.value_float_text = tk.StringVar()
        self.value_float_entry = tk.Entry(value_frame, textvariable=self.value_float_text)
        self.value_float_entry.grid(column=1, row=2)

        value_hex_label = tk.Label(value_frame, text="hex")
        value_hex_label.grid(column=0, row=3)
        self.value_hex_text = tk.StringVar()
        self.value_hex_entry = tk.Entry(value_frame, textvariable=self.value_hex_text)
        self.value_hex_entry.grid(column=1, row=3)

        # main button frame

        new_button_frame = tk.Frame(self.parent)
        new_button_frame.grid(column=0, row=4)
        new_connect_button = tk.Button(
            new_button_frame, text="disconnect", command=self.__disconnect
        )
        new_exit_button = tk.Button(new_button_frame, text="exit", command=self.__exit)
        new_connect_button.grid(column=0, row=0)
        new_exit_button.grid(column=1, row=0)

    def __disconnect(self):
        logging.info("disconnect reaction")

        self.device.disconnect()
        self.parent.withdraw()
        self.config_window.deiconify()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    window = tk.Tk()
    App(window)
    window.mainloop()
