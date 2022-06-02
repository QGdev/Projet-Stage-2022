"""
------------------------------------------------------------------------------------------------------------------------
    Defining application controller

    MIT Licence

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
#   Import of basic modules
import threading
import time
import tkinter as tk
from tkinter import Menu, messagebox
from tkinter import filedialog as fd

#   Import of custom modules
from dataset import DataSet
from import_module import DataImportModule
from model import Model, PlaySpeed
from utils import multiple_svg_path_to_grp_pts, get_color_gradient_array, get_color_hex_array, \
    get_formatted_timestamp_from_value, extract_positive_numerical_value
from views.confirm_config_pop_up import ConfirmConfigPopUp
from views.control_panel_view import ControlPanel
from views.main_view import MainView
from views.sensors_graph_view import SensorsGraphView
from views.sensors_map_view import SensorsMapView

"""

    Controller
    
    In charge of everything important in this application from the startup to the visualisation or the end of it.

"""


class Controller:
    #   View elements
    __window: tk
    __main_view: MainView
    __sensors_map: SensorsMapView
    __sensors_graph: SensorsGraphView
    __control_panel: ControlPanel

    __model: Model | None
    __thread: threading.Thread
    __thread_ask_stop_flag: bool
    __thread_ask_wait_flag: bool
    __thread_wait_status_flag: bool
    __sensor_color_cache: [[str]]
    __timestamp_cache: [str]
    __bg_pts_grps: [[[int, int]]]
    __data_loaded: bool

    """

            CONTROLLER INITIALIZATION SECTION

    """

    #   Controller constructor
    def __init__(self):
        #   Init main window
        self.__window = tk.Tk(className="Soles Data Visualisation")
        self.__window.geometry("800x600")
        self.__window.wm_title("Soles Data Visualisation")
        self.__window.minsize(800, 600)
        self.__window.resizable(True, True)

        #   Init toolbar and main ui
        self.__init_ui__()
        self.__toolbar_init__()

        self.__window.bind('<Configure>', self.on_resize)
        self.__data_loaded = False
        self.__thread_ask_stop_flag = False

    """

            UI INITIALIZATION SECTION

    """

    #   UI Element initialization
    def __init_ui__(self) -> None:
        self.__main_view = MainView(self.__window, self)
        self.__sensors_map = SensorsMapView(self.__main_view.get_top_section(), self)
        self.__sensors_graph = SensorsGraphView(self.__main_view.get_top_section(), self)
        self.__control_panel = ControlPanel(self.__main_view, self,
                                            self.__on_change_play_state,
                                            self.__on_change_play_time,
                                            self.__on_change_play_direction,
                                            self.__on_change_play_speed,
                                            self.__on_change_play_mode,
                                            self.__on_change_custom_time_coef)

        self.__main_view.attach_top_right_widget(self.__sensors_map)
        self.__main_view.attach_top_left_widget(self.__sensors_graph)
        self.__main_view.attach_control_panel(self.__control_panel)

        self.__main_view.pack_top_section()

    #   Initialization of the menubar aka toolbar
    def __toolbar_init__(self) -> None:
        #   Declare file menu
        file_menu = Menu(tearoff=False)

        #   Declare import menu
        import_menu = Menu(file_menu, tearoff=False)
        import_menu.add_command(label="Full data file",
                                command=lambda: self.on_import(DataImportModule.ImportTypes.Full_File))
        import_menu.add_command(label="Data file + SVG file",
                                command=lambda: self.on_import(DataImportModule.ImportTypes.Data_SVG_Files))
        file_menu.add_cascade(label="Import data", menu=import_menu)
        file_menu.add_command(label="Reset", command=self.on_reset)
        file_menu.add_command(label="Exit", command=self.on_exit)

        #   Declare generation menu
        generation_menu = Menu(file_menu, tearoff=False)
        generation_menu.add_command(label="Full data file",
                                    command=lambda: self.on_import(DataImportModule.ImportTypes.Full_File))

        #   Attach the file menu to the menubar
        self.__main_view.set_import_menu("File", file_menu)
        self.__main_view.set_generation_menu("Generate", generation_menu)

    """

            CONTROLLER LAUNCH FUNCTION

    """
    def launch(self) -> None:
        self.__window.mainloop()

    """

            SHORTCUTS FUNCTIONS

    """

    def get_dataset(self) -> DataSet:
        return self.__model.get_dataset()

    def get_model(self) -> Model:
        return self.__model

    """

            CONTROLLER CALLBACK FUNCTIONS INITIALIZATION SECTION (FOR MAIN ACTIONS)

    """

    #   Will be executed when the user ask to import data into the software
    def on_import(self, import_type: DataImportModule.ImportTypes) -> None:
        self.on_reset()

        #   Begin by ask the CSV file which will be  needed in both cases
        filename = fd.askopenfilename(
            title='Open a data file',
            initialdir='~/',
            filetypes=(("CSV Files", ".csv"),))

        #   The user didn't select anything or just close the dialog
        #   So we just abort the function
        if filename == "" or filename == "()":
            messagebox.showerror("CSV file needed",
                                 "You need to select an CSV file to continue")
            return

        import_module: DataImportModule = DataImportModule()

        if import_type == DataImportModule.ImportTypes.Full_File:
            self.__model = import_module.get_model_ff(filename,
                                                      #  On delimiter error, ask user to enter the delimiter
                                                      lambda: self.__main_view.ask_for_csv_settings([("Comma", ','),
                                                                                                     ("Semi-colon", ';'),
                                                                                                     ("Colon", '.'),
                                                                                                     ("Tabulation",
                                                                                                    '\t')]),
                                                      #  On errors that cannot be handled
                                                      lambda x: messagebox.showerror("CSV ERROR",
                                                                                     "An error occurred during the analysis of the given CSV file\n {0}".format(
                                                                                         x)))

            #   An error or an user abortion happened during the import of the file
            #   So we will stop the progression here
            if self.__model is None:
                return

            #   For this type of import there is no bg "image"
            self.__bg_pts_grps = None

        else:
            #   Begin by ask the CSV file which will be  needed in both cases
            filename_svg = fd.askopenfilename(
                title='Open a SVG file',
                initialdir='~/',
                filetypes=(("SVG Files", ".svg"),))
            print(filename_svg)
            #   The user didn't select anything or just close the dialog
            #   So we just abort the function
            if filename_svg == "" or filename_svg == "()":
                messagebox.showerror("SVG file needed",
                                     "You need to select an SVG file to continue")
                return

            importation_result = import_module.get_model_dsf(filename,
                                                             filename_svg,
                                                             #  On delimiter error, ask user to enter the delimiter
                                                             lambda: self.__main_view.ask_for_csv_settings(
                                                                 [("Comma", ','),
                                                                  ("Semi-colon", ';'),
                                                                  ("Colon", '.'),
                                                                  ("Tabulation",
                                                                   '\t')]),
                                                             #  On errors that cannot be handled during SVG analysis
                                                             lambda x: messagebox.showerror("ERROR",
                                                                                            "An error occurred during the analysis of the given SVG file\n {0}".format(x)),
                                                             #  When no background path has been found
                                                             lambda: messagebox.showinfo("No background found",
                                                                                          "The analysis of the SVG haven't revealed background path, don't forget to put \"BG_PATH\" in the id of the path to get a background"),
                                                             #  On errors that cannot be handled during CSV analysis
                                                             lambda x: messagebox.showerror("ERROR",
                                                                                            "An error occurred during the analysis of the given CSV file\n {0}".format(x)))

            #   An error or an user abortion happened during the import of the files
            #   So we will stop the progression here
            if importation_result is None:
                return

            #   Decompose importation result
            self.__model, svg_path_data = importation_result
            self.__bg_pts_grps = multiple_svg_path_to_grp_pts(svg_path_data)

        #   Ask for a confirmation of the deparsed data
        ConfirmConfigPopUp(self.__main_view,
                           #    On confirm, will initialize sensors_map_ui and need to know
                           #    if the y-axis need to be inverted
                           lambda: self.__on_config_confirmed(import_type == DataImportModule.ImportTypes.Full_File),
                           #    If the user simply close or exit the window
                           self.__on_loading_cancel,
                           self.__on_manual_config).show(self.__model.get_dataset())

    #   On window resize event
    def on_resize(self, _: tk.Event) -> None:
        self.__thread_ask_wait_flag = True
        if self.__data_loaded:
            self.__sensors_map.on_resize()
            if self.__bg_pts_grps is not None:
                self.__sensors_map.draw_bg(self.__bg_pts_grps)

            current_step = self.__model.get_current_step_number()
            self.__draw_sensors(len(self.get_dataset().get_sensor_names()),
                                self.__sensor_color_cache[current_step])
            self.__sensors_map.draw_center_of_mass(current_step)

        self.__thread_ask_wait_flag = True

    #   Will be executed everytime the user ask to reset or everytime data is loaded
    def on_reset(self) -> None:
        if self.__data_loaded:
            self.__data_loaded = False
            if self.__thread is not None:
                self.__thread_ask_stop_flag = True
                print("Thread killed...")
                self.__thread.join()

            self.__control_panel.lock_interface()

            self.__control_panel.update_actual_time_label("00:00.000")
            self.__control_panel.update_actual_time_scale(0)
            self.__control_panel.update_end_time_label("00:00.000")
            self.__control_panel.update_end_time_scale(1)

            self.__model = None
            self.__sensors_map.delete('all')
            self.__sensors_graph.clear()

    #   When the window is closed
    def on_exit(self) -> None:
        self.on_reset()
        self.__window.quit()

    """

            VIEW DRAWING SECTION

    """

    def __draw_sensors(self, sensors_number: int, sensors_color: [str]) -> None:
        sensors_names = self.get_dataset().get_sensor_names()
        for i in range(sensors_number):
            self.__sensors_map.draw_sensor(i, sensors_color[i], sensors_names[i])

        self.__sensors_map.draw_sensor_names(self.get_dataset().get_centers(),
                                             sensors_names)

    def __update_sensors(self, step_number: int) -> None:
        sensors_names = self.get_dataset().get_sensor_names()
        sensors_colors = self.__sensor_color_cache[step_number]

        for i in range(self.get_dataset().get_number_of_sensors()):
            self.__sensors_map.update_sensor(sensors_colors[i], sensors_names[i])

    """

            THREADING SECTION

    """

    def __executable_thread(self) -> None:
        self.__thread_ask_stop_flag = False

        #   Check for stop signal
        while not self.__thread_ask_stop_flag:

            #   Don't pass to the next step if the user have set visualization on pause
            if not self.__model.is_paused():

                start_time = time.time()

                current_step = self.__model.get_current_step_number()

                self.__update_sensors(current_step)
                self.__sensors_map.draw_center_of_mass(current_step)

                self.__control_panel.update_actual_time_label(self.__timestamp_cache[current_step])
                self.__control_panel.update_actual_time_scale(current_step)

                #   Put visualisation in pause if a play bound as been reached
                if self.__model.bound_reach():
                    self.__on_change_play_state()

                #   We will check if the drawing time to compare it to the wait time
                #   If the drawing time is greater than the wait time, we skip the wait otherwise we wait
                else:
                    sleep_time = self.__model.get_time_next() - (time.time() - start_time)
                    if sleep_time > 0:
                        time.sleep(sleep_time)

                self.__model.next_step()

    #   Launch the data loading and initialisation processes
    def launch_thread(self) -> None:

        self.__thread = threading.Thread(name="visualization_handler",
                                         target=self.__executable_thread)
        self.__thread.start()
        self.__model.play()

        self.__draw_sensors(self.get_dataset().get_number_of_sensors(),
                            self.__sensor_color_cache[self.__model.get_current_step_number()])
    """
    
        CACHE GENERATION SECTION
        
    """

    #   Will generate the cache containing each color value of each sensor at each period
    def __update_colors_cache(self):
        self.__sensor_color_cache = list()

        for index in range(self.__model.get_steps_number()):

            tmp = self.__model.get_dataset().get_sensors_normalized_values_at(index)
            tmp = get_color_gradient_array(tmp)
            self.__sensor_color_cache.append(get_color_hex_array(tmp))

    #   Will generate the cache containing the formatted timestamp of each period
    def __update_timestamps_cache(self):
        self.__timestamp_cache = list()

        temporal_set = self.get_dataset().get_temporal_set()

        for value in temporal_set:
            self.__timestamp_cache.append(get_formatted_timestamp_from_value(value))

    """

            CONTROLLER CALLBACK FUNCTIONS INITIALIZATION SECTION (FOR IMPORT IN PROGRESS)

    """

    #   Will prepare everything after the loaded configuration has been confirmed
    def __on_config_confirmed(self, y_axis_inverted: bool) -> None:

        self.__sensors_map.update_map_settings(self.get_dataset().get_map_height(),
                                               self.get_dataset().get_map_width(),
                                               y_axis_inverted)
        self.__data_loaded = True

        self.__sensors_map.update_scale_factor()
        self.__sensors_map.update_cache_position()

        if self.__bg_pts_grps is not None:
            self.__sensors_map.draw_bg(self.__bg_pts_grps)

        self.__sensors_graph.plot(self.get_dataset().get_sensors_values(),
                                  self.get_dataset().get_sensor_names(),
                                  self.get_dataset().get_temporal_set())

        self.__update_colors_cache()
        self.__update_timestamps_cache()

        self.__control_panel.update_end_time_label(self.__timestamp_cache[self.__model.get_steps_number() - 1])
        self.__control_panel.update_end_time_scale(self.__model.get_steps_number() - 1)
        self.__control_panel.unlock_time_sliders()
        self.__control_panel.unlock_play_controls()
        self.__control_panel.normal_dir_mode()
        self.__control_panel.realtime_mode()

        self.launch_thread()

    #   When the loaded configuration as been invalidated or canceled
    def __on_loading_cancel(self) -> None:
        #   Model deletion
        if self.__model is not None:
            del self.__model

        #   Thread deletion
        if self.__thread is not None:
            del self.__thread

        #   Reset init flag(s)
        self.__data_loaded = False

    #   This option was basically concepted to let user change settings by hand
    #   Due to lack of time, this was unimplemented
    def __on_manual_config(self) -> None:
        print("manual data config asked !")
        print("NOT IMPLEMENTED !")
        #   TODO: implement on manual config

    """

            CONTROLLER CALLBACK FUNCTIONS INITIALIZATION SECTION (DURING VISUALISATION)

    """
    #   To change from play to pause or vice versa
    def __on_change_play_state(self) -> None:
        if self.__model.is_paused():
            self.__model.play()

            if self.__model.bound_reach():
                if self.__model.end_has_been_reached() and self.__model.is_normal_play():
                    self.__on_change_play_direction("reverse")
                else:
                    self.__on_change_play_direction("normal")

            self.launch_thread()
        else:
            self.__model.pause()
            self.__thread_ask_stop_flag = True

    #   Will handle jump to time or go to start/end or previous/next frame operations during visualisation
    def __on_change_play_time(self, operation: str, new_time: int = -1) -> None:
        self.__thread_ask_wait_flag = True

        if operation == "jump":
            if new_time > -1:
                self.__model.jump_to_step(new_time)
        else:
            if operation == "go_start":
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
                    self.__thread_ask_stop_flag = False
                    raise Exception("on_change_play_time : UNSUPPORTED INSTRUCTION ({:s})".format(operation))
            else:
                self.__thread_ask_stop_flag = False
                raise Exception("on_change_play_time : UNSUPPORTED INSTRUCTION ({:s})".format(operation))

            #   Update the time scale for any operation except for the jump operation because
            #   it will cause a weird recursion error for some reason that is a working fix
            self.__control_panel.update_actual_time_scale(self.__model.get_current_step_number())

        self.__thread_ask_wait_flag = False

        current_step_number = self.__model.get_current_step_number()

        self.__update_sensors(current_step_number)
        self.__sensors_map.draw_center_of_mass(current_step_number)
        self.__control_panel.update_actual_time_label(self.__timestamp_cache[current_step_number])

    #   To handle change of the play direction normal or reverse
    def __on_change_play_direction(self, direction: str) -> None:
        if direction == "reverse":
            self.__model.reverse()
            self.__control_panel.reverse_dir_mode()
        else:
            self.__model.normal()
            self.__control_panel.normal_dir_mode()

    #   Change speed coef from menu (for realtime time coef only)
    def __on_change_play_speed(self, index: int) -> None:
        self.__model.set_play_speed(list(PlaySpeed)[index].value[0])

    #   Change from real-time coef to custom coef
    def __on_change_play_mode(self, operation: str) -> None:
        if operation == "real-time":
            self.__model.enable_realtime()
            self.__control_panel.realtime_mode()
        elif operation == "custom":
            self.__model.enable_custom_speed_factor()
            self.__control_panel.custom_time_coef_mode()
        else:
            raise Exception("__on_change_play_mode : UNSUPPORTED INSTRUCTION ({:s})".format(operation))
        self.__control_panel.update()

    #   Change speed coef from entry (for custom time coef only)
    def __on_change_custom_time_coef(self, new_frame_time: str) -> None:
        value = extract_positive_numerical_value(new_frame_time)
        if value is None or value <= 0:
            messagebox.showerror("Wrong value entered",
                                 "The value can be a decimal point value but must be positive and non null")
            self.__control_panel.change_frame_time_entry_to_red()
            time.sleep(1)
            self.__control_panel.reset_custom_time_coef_entry_color()
            self.__control_panel.set_custom_time_coef_entry_content(str(self.__model.get_play_speed_factor()))

        else:
            self.__model.set_speed_factor_value(value)
