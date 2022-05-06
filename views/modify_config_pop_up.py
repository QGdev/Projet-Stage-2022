"""
------------------------------------------------------------------------------------------------------------------------
    Defining the pop up that will allow the user to modify configuration

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
from tkinter import Frame, Toplevel, Label, Button, StringVar

from dataset import DataSet


class ModifyConfigPopUp(Toplevel):

    __on_confirm: 'function'
    __on_cancel: 'function'

    def __init__(self, parent, on_confirm, on_cancel):
        super().__init__(parent)
        self.wm_title("Modify configuration")
        self.resizable(False, False)

        self.__on_confirm = on_confirm
        self.__on_cancel = on_cancel

    def show(self, dataset: DataSet):

        sensors_positions = dataset.get_positions()
        sensors_names = dataset.get_sensor_names()
        sensors_max_norm = dataset.get_sensors_max()
        sensors_min_norm = dataset.get_sensors_min()
        sensors_max = dataset.get_sensors_max_denormalized()
        sensors_min = dataset.get_sensors_min_denormalized()
        sensors_number = len(sensors_names)

        head_message = Label(self, text="Modify configuration attributes")
        head_message.grid(row=1, column=1, columnspan=3, padx=20, pady=20, sticky='nswe')

        array_frame = Frame(self)
        array_frame.config(borderwidth=2, bg="light gray")

        #   Set array header (column titles)
        array_head_name = Label(array_frame, text="Names", borderwidth=1, bg='light grey', relief='ridge')
        array_head_name.grid(row=0, column=0, columnspan=1, sticky='nswe', ipadx=20)

        array_head_position = Label(array_frame, text="Positions", borderwidth=1, bg='light grey', relief='ridge')
        array_head_position.grid(row=0, column=1, columnspan=2, sticky='nswe', ipadx=20)

        array_head_max = Label(array_frame, text="Max (norm.)", borderwidth=1, bg='light grey', relief='ridge')
        array_head_max.grid(row=0, column=3, columnspan=1, sticky='nswe', ipadx=20)

        array_head_min = Label(array_frame, text="Min (norm.)", borderwidth=1, bg='light grey', relief='ridge')
        array_head_min.grid(row=0, column=4, columnspan=1, sticky='nswe', ipadx=20)

        array_head_max = Label(array_frame, text="Max", borderwidth=1, bg='light grey', relief='ridge')
        array_head_max.grid(row=0, column=5, columnspan=1, sticky='nswe', ipadx=20)

        array_head_min = Label(array_frame, text="Min", borderwidth=1, bg='light grey', relief='ridge')
        array_head_min.grid(row=0, column=6, columnspan=1, sticky='nswe', ipadx=20)

        #   Draw a line for each sensor displaying name, position, min and max for normalized and non normalized values
        for i in range(len(dataset.get_sensor_set())):
            Label(array_frame,
                  text=sensors_names[i],
                  borderwidth=1,
                  bg='white',
                  relief='ridge').grid(row=i + 1,
                                       column=0,
                                       columnspan=1,
                                       sticky='nswe', ipadx=10)
            Label(array_frame,
                  text=sensors_positions[i].to_string(),
                  borderwidth=1,
                  bg='white',
                  relief='ridge').grid(row=i + 1,
                                       column=1,
                                       columnspan=2,
                                       sticky='nswe', ipadx=10)
            Label(array_frame,
                  text="{:.6f}".format(sensors_max_norm[i]),
                  borderwidth=1,
                  bg='white',
                  relief='ridge').grid(row=i + 1,
                                       column=3,
                                       columnspan=1,
                                       sticky='nswe', ipadx=10)
            Label(array_frame,
                  text="{:.6f}".format(sensors_min_norm[i]),
                  borderwidth=1,
                  bg='white',
                  relief='ridge').grid(row=i + 1,
                                       column=4,
                                       columnspan=1,
                                       sticky='nswe', ipadx=10)
            Label(array_frame,
                  text="{:.3f}".format(sensors_max[i]),
                  borderwidth=1,
                  bg='white',
                  relief='ridge').grid(row=i + 1,
                                       column=5,
                                       columnspan=1,
                                       sticky='nswe', ipadx=10)
            Label(array_frame,
                  text="{:.3f}".format(sensors_min[i]),
                  borderwidth=1,
                  bg='white',
                  relief='ridge').grid(row=i + 1,
                                       column=6,
                                       columnspan=1,
                                       sticky='nswe', ipadx=10)

            #   Add a line where map dimension will be showed
            array_head_map_dims = Label(array_frame, text="Map dimensions", borderwidth=1, bg='light grey',
                                        relief='ridge')
            array_head_map_dims.grid(row=sensors_number + 1, column=0, columnspan=1, sticky='nswe', ipadx=20)

            Label(array_frame,
                  text="Width: {:d}\tHeight: {:d}".format(dataset.get_map_width(), dataset.get_map_height()),
                  borderwidth=1,
                  bg='white',
                  relief='ridge').grid(row=sensors_number + 1,
                                       column=1,
                                       columnspan=2,
                                       sticky='nswe', ipadx=20)

        #   Show the array
        array_frame.grid(row=2, column=1, columnspan=3, padx=20, pady=20, sticky='nswe')

        #   Just here to acquire the pressed button
        button_pressed = StringVar()

        #   Init buttons
        #   Just cancel the import
        Button(self,
               text="Cancel",
               command=lambda: button_pressed.set("cancel")).grid(row=3,
                                                                  column=1,
                                                                  padx=20,
                                                                  pady=20,
                                                                  sticky='nswe')
        #   Let the user adjust sensors configuration
        Button(self,
               text="Set configuration manually",
               command=lambda: button_pressed.set("config")).grid(row=3,
                                                                  column=2,
                                                                  padx=20,
                                                                  pady=20,
                                                                  sticky='nswe')
        #   Just launch the visualisation
        Button(self,
               text="Next",
               command=lambda: button_pressed.set("next")).grid(row=3,
                                                                column=3,
                                                                padx=20,
                                                                pady=20,
                                                                sticky='nswe')
        #   Halt the execution, wait a button press
        self.wait_variable(button_pressed)
        self.destroy()

        if button_pressed.get() == "cancel":
            self.__on_cancel()
        elif button_pressed.get() == "config":
            self.__on_manual_config()
        else:
            self.__on_confirm()
