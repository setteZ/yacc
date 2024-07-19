"""
Structure for a CAN GUI
"""

import argparse
import logging
import tkinter as tk


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

        self.__populate_window()

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

    def __populate_window(self):
        """
        function to create the config window
        """

        self.parent.title("Hello")
        self.parent.resizable(False, False)
        self.parent.configure(background="white")

        file_frame = tk.LabelFrame(self.parent, text="file")
        file_frame.grid(column=0, row=0)

        file_entry = tk.Entry(file_frame)
        file_button = tk.Button(file_frame, text="select file")
        file_entry.pack()
        file_button.pack()

        interface_frame = tk.LabelFrame(self.parent, text="interface")
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

        baudrate_frame = tk.LabelFrame(self.parent, text="baudrate")
        baudrate_frame.grid(column=0, row=2)
        baudrate_list = ["125", "250", "500"]
        self.variable_br = tk.StringVar(baudrate_frame)
        self.variable_br.set(baudrate_list[1])
        baudrate_opt = tk.OptionMenu(baudrate_frame, self.variable_br, *baudrate_list)
        baudrate_opt.config(font=("Helvetica", 12))
        baudrate_opt.pack()

        self.variable_br.trace("w", self.__callback_br)

        nodeid_frame = tk.LabelFrame(self.parent, text="node id")
        nodeid_frame.grid(column=0, row=3)
        nodeid_entry = tk.Entry(nodeid_frame)
        nodeid_entry.pack()

        button_frame = tk.Frame(self.parent)
        button_frame.grid(column=0, row=4)
        connect_button = tk.Button(
            button_frame, text="connect", command=self.create_new_window
        )
        exit_button = tk.Button(button_frame, text="exit", command=self.parent.destroy)
        connect_button.grid(column=0, row=0)
        exit_button.grid(column=1, row=0)

    def __callback_ele(self, *args):
        """
        callback for element selection
        """
        element = self.variable_ele.get()
        self.idx_text.set(element)

    def __callback_grp(self, *args):
        """
        callback for group selection
        """
        group = self.variable_grp.get()
        self.sub_text.set(group)

    def __entry_typing(self, *args):
        """
        entry_typing reaction
        """
        logging.info("entry typing reaction")

    def __read_action(self, *args):
        logging.info("read action")

    def __write_action(self, *args):
        logging.info("write action")

    def create_new_window(self):
        """
        new window creation after "connect" button is clicked
        """
        self.parent.destroy()
        new_window = tk.Tk()

        # entry frame
        entry_frame = tk.Frame(new_window)
        entry_frame.grid(column=0, row=0)
        ## element
        element_frame = tk.LabelFrame(entry_frame, text="element")
        element_frame.grid(column=0, row=0)
        element_list = ["element1", "element2", "element3"]
        self.variable_ele = tk.StringVar(element_frame)
        self.variable_ele.set(element_list[1])
        element_opt = tk.OptionMenu(element_frame, self.variable_ele, *element_list)
        element_opt.config(font=("Helvetica", 12))
        element_opt.pack()

        self.variable_ele.trace("w", self.__callback_ele)

        ## group
        group_frame = tk.LabelFrame(entry_frame, text="group")
        group_frame.grid(column=1, row=0)
        group_list = ["group1", "group2", "group3"]
        self.variable_grp = tk.StringVar(group_frame)
        self.variable_grp.set(group_list[1])
        group_opt = tk.OptionMenu(group_frame, self.variable_grp, *group_list)
        group_opt.config(font=("Helvetica", 12))
        group_opt.pack()

        self.variable_grp.trace("w", self.__callback_grp)

        ## idx
        self.idx_text = tk.StringVar()
        idx_frame = tk.LabelFrame(entry_frame, text="idx")
        idx_frame.grid(column=0, row=1)
        idx_entry = tk.Entry(idx_frame, textvariable=self.idx_text)

        idx_entry.bind("<Key>", self.__entry_typing)
        idx_entry.pack()

        ## sub
        self.sub_text = tk.StringVar()
        sub_frame = tk.LabelFrame(entry_frame, text="sub")
        sub_frame.grid(column=1, row=1)
        sub_entry = tk.Entry(sub_frame, textvariable=self.sub_text)
        sub_entry.pack()

        # command frame
        command_frame = tk.Frame(new_window)
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
        data_frame = tk.Frame(new_window)
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

        value_uint_label = tk.Label(value_frame, text="uint")
        value_uint_label.grid(column=0, row=0)
        value_uint_text = tk.StringVar()
        value_uint_entry = tk.Entry(value_frame, textvariable=value_uint_text)
        value_uint_entry.grid(column=1, row=0)

        value_int_label = tk.Label(value_frame, text="int")
        value_int_label.grid(column=0, row=1)
        value_int_text = tk.StringVar()
        value_int_entry = tk.Entry(value_frame, textvariable=value_int_text)
        value_int_entry.grid(column=1, row=1)

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

        new_button_frame = tk.Frame(new_window)
        new_button_frame.grid(column=0, row=4)
        new_connect_button = tk.Button(
            new_button_frame, text="disconnect", command=new_window.destroy
        )
        new_exit_button = tk.Button(
            new_button_frame, text="exit", command=new_window.destroy
        )
        new_connect_button.grid(column=0, row=0)
        new_exit_button.grid(column=1, row=0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--info", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    logging_level = logging.NOTSET
    if args.debug:
        print("debug")
        logging_level = logging.DEBUG
    if args.info:
        print("info")
        logging_level = logging.INFO

    logging.getLogger().setLevel(logging_level)

    window = tk.Tk()
    MainApplication(window)
    window.mainloop()
