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
from model import Model, PlaySpeed
from position import Position
from views.confirm_config_pop_up import ConfirmConfigPopUp
from views.control_panel_ui import ControlPanelUI
from views.main_ui import MainUI
from views.sensors_graph_ui import SensorsGraphUI
from views.sensors_map_ui import SensorsMapUI
from utils import get_color_hex, get_color_from_gradient, extract_numerical_value


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
        self.__data_loaded = False
        self.__thread_ask_stop_flag = False

    #   UI Element initialization
    def __ui_init__(self):
        self.__main_ui = MainUI(self.__window, self)
        self.__sensors_map = SensorsMapUI(self.__main_ui.get_top_section(), self)
        self.__control_panel = ControlPanelUI(self.__main_ui, self,
                                              self.__on_change_play_state,
                                              self.__on_change_play_time,
                                              self.__on_change_play_direction,
                                              self.__on_change_play_speed,
                                              self.__on_change_play_mode,
                                              self.__on_change_frame_time)

        test = SensorsGraphUI(self.__main_ui.get_top_section(), self)
        self.__main_ui.attach_top_left_widget(test)
        test.plot()

        self.__main_ui.attach_top_right_widget(self.__sensors_map)
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
        file_menu.add_command(label="Reset", command=self.on_reset)
        file_menu.add_command(label="Exit", command=self.on_exit)

        #   Attach the file menu to the menubar
        menubar.add_cascade(label="File", menu=file_menu)

    def on_import(self, import_type: DataImportModule.ImportTypes):

        self.on_reset()

        #   Begin by ask the CSV file which will be  needed in both cases
        filename = fd.askopenfilename(
            title='Open a data file',
            initialdir='~/',
            filetypes=(("CSV Files", ".csv"),))

        #   The user didn't select anything or just close the dialog
        #   So we just abort the function
        if filename == "" or filename == "()":
            return

        import_module: DataImportModule = DataImportModule()

        if import_type == DataImportModule.ImportTypes.Full_File:
            self.__model = import_module.get_model_ff(filename,
                                                      #  On delimiter error, ask user to enter the delimiter
                                                      lambda: self.__main_ui.ask_for_csv_settings([("Comma", ','),
                                                                                                   ("Semi-colon", ';'),
                                                                                                   ("Colon", '.'),
                                                                                                   ("Tabulation", '\t')]),
                                                      #  On errors that cannot be handled
                                                      lambda x: messagebox.showerror("CSV ERROR",
                                                                                     "An error occurred during the analysis of the given CSV file\n {0}".format(x)))
        else:
            #   Begin by ask the CSV file which will be  needed in both cases
            filename_svg = fd.askopenfilename(
                title='Open a SVG file',
                initialdir='~/',
                filetypes=(("SVG Files", ".svg"),))

            #   The user didn't select anything or just close the dialog
            #   So we just abort the function
            if filename_svg == "" or filename_svg == "()":
                messagebox.showerror("CSV file needed",
                                     "You need to select an SVG file to continue")
                return

            self.__model = import_module.get_model_dsf(filename,
                                                       filename_svg,
                                                       #  On delimiter error, ask user to enter the delimiter
                                                       lambda: self.__main_ui.ask_for_csv_settings([("Comma", ','),
                                                                                                    ("Semi-colon", ';'),
                                                                                                    ("Colon", '.'),
                                                                                                    ("Tabulation", '\t')]),
                                                       #  On errors that cannot be handled during SVG analysis
                                                       lambda x: messagebox.showerror("ERROR",
                                                                                      "An error occurred during the analysis of the given SVG file\n {0}".format(x)),
                                                       #  On errors that cannot be handled during CSV analysis
                                                       lambda x: messagebox.showerror("ERROR",
                                                                                      "An error occurred during the analysis of the given CSV file\n {0}".format(x)))

        #   An error or an user abortion happened during the import of the file
        #   So we will stop the progression here
        if self.__model is None:
            return

        #   Ask for a confirmation of the deparsed data
        ConfirmConfigPopUp(self.__main_ui,
                           #    On confirm, will initialize sensors_map_ui and need to know
                           #    if the y-axis need to be inverted
                           lambda: self.__on_config_confirmed(import_type == DataImportModule.ImportTypes.Full_File),
                           #    If the user simply close or exit the window
                           self.__on_loading_cancel,
                           self.__on_manual_config).show(self.__model.get_dataset())

    def on_reset(self):
        if self.__data_loaded:
            if self.__thread is not None:
                self.__thread_ask_stop_flag = True
                print("Thread killed...")
                self.__thread.join()
            self.__control_panel.lock_interface()
            self.__control_panel.update_actual_time(0)
            self.__control_panel.update_end_time(0)
            del self.__model
            self.__sensors_map.delete('all')

    def on_exit(self):
        if self.__data_loaded:
            if self.__thread is not None:
                self.__thread_ask_stop_flag = True
                print("Thread killed...")
                self.__thread.join()
            self.__control_panel.lock_interface()
            self.__control_panel.update_actual_time(0)
            self.__control_panel.update_end_time(0)
            del self.__model
            self.__sensors_map.delete('all')
        self.__window.quit()


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

                time.sleep(self.__model.get_time_next())

                self.__model.next_step()

    #   Launch the data loading and initialisation processes
    def launch_thread(self) -> None:
        self.__thread = threading.Thread(name='"visualization_handler"',
                                         target=self.__executable_thread)
        self.__control_panel.lock_normal_dir_button()

        self.__sensors_map.update_scale_factor()
        self.__thread.start()
        self.__model.play_normal()
        self.__model.play()

    def __on_config_confirmed(self, y_axis_inverted: bool) -> None:
        self.__sensors_map.update_map_settings(self.get_dataset().get_map_height(),
                                               self.get_dataset().get_map_width(),
                                               y_axis_inverted)
        self.__data_loaded = True
        self.launch_thread()
        self.__control_panel.update_end_time(self.__model.get_steps_number() - 1)
        self.__control_panel.unlock_sliders()
        self.__control_panel.unlock_play_controls()
        self.__control_panel.lock_normal_dir_button()
        self.__control_panel.realtime_mode()

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
        self.__thread_ask_wait_flag = True
        if self.__data_loaded:
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
        self.__control_panel.update_actual_time(self.__model.get_current_step_number())

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

    def __on_change_play_speed(self, index: int) -> None:
        self.__model.set_play_speed(list(PlaySpeed)[index].value[0])
        self.__control_panel.update()

    def __on_change_play_mode(self, operation: str) -> None:
        if operation == "real-time":
            self.__model.enable_realtime()
            self.__control_panel.realtime_mode()
        elif operation == "custom":
            self.__model.enable_custom_delay()
            self.__control_panel.custom_frame_time_mode()
        else:
            raise Exception("__on_change_play_mode : UNSUPPORTED INSTRUCTION ({:s})".format(operation))
        self.__control_panel.update()

    def __on_change_frame_time(self, new_frame_time: str) -> None:
        value = extract_numerical_value(new_frame_time)
        if value is None or value <= 0:
            messagebox.showerror("Wrong value entered",
                                 "The value can be a decimal point value but must be positive and non null")
            self.__control_panel.change_frame_time_entry_to_red()
            time.sleep(0.75)
            self.__control_panel.reset_frame_time_entry_color()
            self.__control_panel.set_frame_time_entry_content(self.__model.get_frame_time())

        self.__model.set_frame_time_value(value)
        self.__control_panel.update()
