"""
Structure for a CAN GUI
"""

import argparse
import logging
import os
import tkinter as tk
from tkinter import filedialog as fd


class MainApplication(tk.Frame):
    """
    window creation for CAN configuration
    """

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.variable_ele = None
        self.variable_grp = None
        self.idx_text = None
        self.sub_text = None
        self.file_str_entry = None
        self.variable_node = None

        self.parent.title("")
        self.parent.resizable(False, False)
        self.__populate_parent()
        self.parent.withdraw()
        self.config_window = tk.Tk()
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
        INTERFACE = interface_list[0]
        self.interface_variable.set(INTERFACE)
        interface_opt = tk.OptionMenu(
            interface_frame, self.interface_variable, *interface_list
        )
        interface_opt.config(font=("Helvetica", 12))
        interface_opt.pack()

        self.interface_variable.trace("w", self.__callback_itf)

        baudrate_frame = tk.LabelFrame(self.config_window, text="baudrate")
        baudrate_frame.grid(column=0, row=2)
        baudrate_list = ["125", "250", "500"]
        self.variable_br = tk.StringVar(baudrate_frame)
        self.variable_br.set(baudrate_list[1])
        baudrate_opt = tk.OptionMenu(baudrate_frame, self.variable_br, *baudrate_list)
        baudrate_opt.config(font=("Helvetica", 12))
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
            self.idx_text.set(element)

    def __callback_grp(self, *args):
        """
        callback for group selection
        """
        group = self.variable_grp.get()
        if group != "":
            self.sub_text.set(group)

    def __entry_typing(self, *args):
        """
        entry_typing reaction
        """
        logging.info("entry: idx %s sub %s", self.idx_text.get(), self.sub_text.get())
        self.variable_grp.set("")
        self.variable_ele.set("")

    def __read_action(self):
        logging.info("read action")

    def __write_action(self):
        logging.info("write action")

    def __connect(self):
        """
        new window creation after "connect" button is clicked
        """
        self.config_window.withdraw()

        # TODO pass the config params to create the connection to the CAN device

        logging.info(
            "interface = %s | baudrate = %s | node-id = %s | eds = %s",
            self.interface_variable.get(),
            self.variable_br.get(),
            self.variable_node.get(),
            self.file_str_entry.get(),
        )

        self.parent.deiconify()

    def __populate_parent(self):
        """
        function to populate the main app window
        """

        # entry frame
        entry_frame = tk.Frame(self.parent)
        entry_frame.grid(column=0, row=0)
        ## element
        element_frame = tk.LabelFrame(entry_frame, text="element")
        element_frame.grid(column=0, row=0)
        element_list = ["element1", "element2", "element3"]
        self.variable_ele = tk.StringVar(element_frame)
        self.variable_ele.set("")
        element_opt = tk.OptionMenu(element_frame, self.variable_ele, *element_list)
        element_opt.config(font=("Helvetica", 12))
        element_opt.pack()

        self.variable_ele.trace("w", self.__callback_ele)

        ## group
        group_frame = tk.LabelFrame(entry_frame, text="group")
        group_frame.grid(column=1, row=0)
        group_list = ["group1", "group2", "group3"]
        self.variable_grp = tk.StringVar(group_frame)
        self.variable_grp.set("")
        group_opt = tk.OptionMenu(group_frame, self.variable_grp, *group_list)
        group_opt.config(font=("Helvetica", 12))
        group_opt.pack()

        self.variable_grp.trace("w", self.__callback_grp)

        ## idx
        idx_frame = tk.LabelFrame(entry_frame, text="idx")
        idx_frame.grid(column=0, row=1)
        self.idx_text = tk.StringVar(idx_frame)
        idx_entry = tk.Entry(idx_frame, textvariable=self.idx_text)

        idx_entry.bind("<Key>", self.__entry_typing)
        idx_entry.pack()

        ## sub
        self.sub_text = tk.StringVar()
        sub_frame = tk.LabelFrame(entry_frame, text="sub")
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

        # data frame
        data_frame = tk.Frame(self.parent)
        data_frame.grid(column=2, row=0)

        ## length
        length_text = tk.StringVar()
        length_frame = tk.LabelFrame(data_frame, text="length")
        length_frame.grid(column=0, row=0)
        length_entry = tk.Entry(length_frame, textvariable=length_text)

        length_entry.pack()

        ## value
        value_frame = tk.LabelFrame(data_frame, text="value")
        value_frame.grid(column=0, row=1)

        value_unsigned_label = tk.Label(value_frame, text="unsigned")
        value_unsigned_label.grid(column=0, row=0)
        value_unsigned_text = tk.StringVar()
        value_unsigned_entry = tk.Entry(value_frame, textvariable=value_unsigned_text)
        value_unsigned_entry.grid(column=1, row=0)

        value_signed_label = tk.Label(value_frame, text="signed")
        value_signed_label.grid(column=0, row=1)
        value_signed_text = tk.StringVar()
        value_signed_entry = tk.Entry(value_frame, textvariable=value_signed_text)
        value_signed_entry.grid(column=1, row=1)

        value_hex_label = tk.Label(value_frame, text="hex")
        value_hex_label.grid(column=0, row=2)
        value_hex_text = tk.StringVar()
        value_hex_entry = tk.Entry(value_frame, textvariable=value_hex_text)
        value_hex_entry.grid(column=1, row=2)

        value_float_label = tk.Label(value_frame, text="float")
        value_float_label.grid(column=0, row=3)
        value_float_text = tk.StringVar()
        value_float_entry = tk.Entry(value_frame, textvariable=value_float_text)
        value_float_entry.grid(column=1, row=3)

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
        # TODO disconnect from the CAN device

        self.parent.withdraw()
        self.config_window.deiconify()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--info", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    logging_level = logging.NOTSET
    if args.debug:
        logging_level = logging.DEBUG
    if args.info:
        logging_level = logging.INFO

    logging.getLogger().setLevel(logging_level)

    window = tk.Tk()
    MainApplication(window)
    window.mainloop()
