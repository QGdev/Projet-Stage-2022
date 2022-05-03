"""
------------------------------------------------------------------------------------------------------------------------
    Defining application controller

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
import threading
import time
import tkinter as tk
from tkinter import Menu, messagebox
from tkinter import filedialog as fd

from dataset import DataSet
from import_module import DataImportModule
from model import Model
from position import Position
from ui.confirm_config_pop_up import ConfirmConfigPopUp
from ui.control_panel_ui import ControlPanelUI
from ui.main_ui import MainUI
from ui.sensors_map_ui import SensorsMapUI
from utils import get_color_hex, get_color_from_gradient


class Controller:
    __window: tk
    __main_ui: 'MainUI'
    __sensors_map: SensorsMapUI
    __control_panel: ControlPanelUI

    __model: 'Model'
    __thread: threading.Thread
    __thread_ask_stop_flag: bool
    __thread_ask_wait_flag: bool
    __thread_wait_status_flag: bool
    __data_loaded: bool

    #   Controller constructor
    def __init__(self):
        self.__window = tk.Tk(className="Soles Data Visualisation")
        self.__window.geometry("800x600")
        self.__window.wm_title("Soles Data Visualisation")
        self.__window.minsize(800, 600)
        self.__window.resizable(True, True)
        self.__ui_init__()
        self.__toolbar_init__()

        self.__window.bind('<Configure>', self.on_resize)
        self.__thread_ask_stop_flag = False

    #   UI Element initialization
    def __ui_init__(self):
        self.__main_ui = MainUI(self.__window, self)
        self.__sensors_map = SensorsMapUI(self.__main_ui.get_top_section(), self)
        self.__control_panel = ControlPanelUI(self.__main_ui, self,
                                              self.__on_change_play_state,
                                              self.__on_change_play_time,
                                              self.__on_change_play_direction,
                                              self.__on_change_play_speed)

        self.__main_ui.attach_sensors_map(self.__sensors_map)
        self.__main_ui.attach_control_panel(self.__control_panel)

        self.__main_ui.pack_top_section()

    #   Initialization of the menubar aka toolbar
    def __toolbar_init__(self):
        #   Declare menubar
        menubar = Menu(self.__window)
        self.__window.config(menu=menubar)

        #   Declare file menu
        file_menu = Menu(menubar, tearoff=0)

        #   Declare import menu
        import_menu = Menu(file_menu, tearoff=0)
        import_menu.add_command(label="Full data file",
                                command=lambda: self.on_import(DataImportModule.ImportTypes.Full_File))
        import_menu.add_command(label="Data file + SVG file",
                                command=lambda: self.on_import(DataImportModule.ImportTypes.Data_SVG_Files))

        file_menu.add_cascade(label="Import data", menu=import_menu)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Exit", command=self.on_exit)

        #   Attach the file menu to the menubar
        menubar.add_cascade(label="File", menu=file_menu)

    def on_import(self, import_type: DataImportModule.ImportTypes):
        filename = fd.askopenfilename(
            title='Open a data file',
            initialdir='~/',
            filetypes=(("CSV Files", ".csv"),))

        #   The user didn't select anything or just close the dialog
        #   So we just abort the function
        if filename == "" or filename == "()":
            return

        importModule: DataImportModule = DataImportModule()

        self.__model = importModule.get_model_ff_csv(filename,
                                                     #  On delimiter error, ask user to enter the delimiter
                                                     lambda: self.__main_ui.ask_for_csv_settings([("Comma", ','),
                                                                                                  ("Semi-colon", ';'),
                                                                                                  ("Colon", '.'),
                                                                                                  ("Tabulation", '\t')]),
                                                     #  On errors that cannot be handled
                                                     lambda x: messagebox.showerror("CSV ERROR",
                                                                                    "An error occurred during the analysis of the given CSV file\n {0}".format(x)))
        #   An error or an user abortion happened during the import of the file
        #   So we will stop the progression here
        if self.__model is None:
            return

        #   Ask for a confirmation of the deparsed data
        ConfirmConfigPopUp(self.__main_ui,
                           self.__on_config_confirmed,
                           self.__on_loading_cancel,
                           self.__on_manual_config).show(self.__model.get_dataset())

    def on_exit(self):
        self.__thread_ask_stop_flag = True
        self.__window.quit()

    #   Launch the data loading and initialisation processes

    def __draw_sensors(self, sensors_number: int, sensors_data: [float]):
        for i in range(sensors_number):
            self.__sensors_map.draw_sensor(i, get_color_hex(get_color_from_gradient(sensors_data[i])))
        self.__sensors_map.update()

    def __executable_thread(self):
        self.__thread_ask_stop_flag = False

        sensors_positions: [Position] = self.__model.get_positions()
        sensors_number: int = len(sensors_positions)
        sensors_data: [float]

        self.__sensors_map.update_cache()

        #   Check for stop signal
        while not self.__thread_ask_stop_flag:

            #   Don't pass to the next step if the user have set visualization on pause
            if not self.__model.is_paused():
                self.__draw_sensors(sensors_number, self.__model.get_current_step_data())
                self.__control_panel.update_actual_time(self.__model.get_current_step_number())
                time.sleep(self.__model.get_delta_time_next() * 0.001 * self.__model.get_play_speed_factor())

                self.__model.next_step()

    def launch_thread(self) -> None:
        self.__thread = threading.Thread(name='"visualization_handler"',
                                         target=self.__executable_thread)
        self.__sensors_map.update_scale_factor()
        self.__thread.start()
        self.__model.play_normal()
        self.__model.play()

    def __on_config_confirmed(self) -> None:
        self.__sensors_map.update_map_settings(self.get_dataset().get_map_height(),
                                               self.get_dataset().get_map_width(),
                                               10, 10)
        self.launch_thread()
        self.__control_panel.update_end_time(self.__model.get_steps_number() - 1)
        self.__control_panel.update_speed_slider_value(self.__model.get_play_speed())
        self.__control_panel.update_speed_value(self.__model.get_play_speed())
        self.__control_panel.unlock_sliders()
        self.__control_panel.unlock_play_controls()

    def __on_loading_cancel(self) -> None:
        #   Model deletion
        if self.__model is not None:
            del self.__model

        #   Thread deletion
        if self.__thread is not None:
            del self.__thread

        #   Reset init flag(s)
        self.__data_loaded = False

    def __on_manual_config(self):
        print("manual data config asked !")
        print("BUT WILL DO NOTHING FOR NOW !")
        #   TODO: implement on manual config

    def on_resize(self, event: tk.Event):
        print(event)
        self.__thread_ask_wait_flag = True
        self.__sensors_map.on_resize()
        self.__thread_ask_wait_flag = False

    def launch(self):
        self.__window.mainloop()

    def get_dataset(self) -> DataSet:
        return self.__model.get_dataset()

    def get_model(self) -> Model:
        return self.__model

    def __on_change_play_state(self) -> None:
        if self.__model.is_paused():
            self.__model.play()
            self.launch_thread()
        else:
            self.__model.pause()
            self.__thread_ask_stop_flag = True

    def __on_change_play_time(self, operation: str, new_time: int = -1) -> None:
        if operation == "jump":
            if new_time > -1:
                self.__model.jump_to_step(new_time)

        elif operation == "go_start":
            self.__model.jump_to_step(0)

        elif operation == "go_end":
            self.__model.jump_to_step(self.__model.get_steps_number() - 1)

        #   Next and previous frame operations are only supported when the visualization is stopped
        elif self.__model.is_paused():
            if operation == "previous_frame":
                self.__model.jump_to_step(self.__model.get_current_step_number() - 1)

            elif operation == "next_frame":
                self.__model.jump_to_step(self.__model.get_current_step_number() + 1)

            else:
                raise Exception("on_change_play_time : UNSUPPORTED INSTRUCTION ({:s})".format(operation))
        else:
            raise Exception("on_change_play_time : UNSUPPORTED INSTRUCTION ({:s})".format(operation))

        self.__draw_sensors(len(self.__model.get_dataset().get_sensor_names()),
                            self.__model.get_current_step_data())
        self.__control_panel.update_time_slider_value(self.__model.get_current_step_number())
        self.__control_panel.update()

    def __on_change_play_direction(self, direction: str) -> None:
        if direction == "reverse":
            self.__model.play_reverse()
            self.__control_panel.unlock_normal_dir_button()
            self.__control_panel.lock_reverse_dir_button()
        else:
            self.__model.play_normal()
            self.__control_panel.unlock_reverse_dir_button()
            self.__control_panel.lock_normal_dir_button()

        self.__control_panel.update()

    def __on_change_play_speed(self, new_speed: float) -> None:
        self.__model.set_play_speed(new_speed)
        self.__control_panel.update()
