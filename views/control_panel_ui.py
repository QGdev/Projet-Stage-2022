"""
------------------------------------------------------------------------------------------------------------------------
    Defining control panel frame

    STAGE 521 - 522
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
from tkinter import Frame, Label, Button, Scale, IntVar, LabelFrame, OptionMenu, StringVar, Entry
from model import PlaySpeed
from utils import update_slider_max, unlock, lock


class ControlPanelUI(Frame):
    __controller: 'Controller'

    __on_change_play_state: 'function'
    __on_change_play_time: 'function'
    __on_change_play_direction: 'function'
    __on_change_play_speed: 'function'
    __on_change_play_mode: 'function'
    __on_change_frame_time: 'function'

    __actual_time_label: Label
    __total_time_label: Label

    __play_pause_button: Button
    __go_start_button: Button
    __go_end_button: Button
    __next_frame_button: Button
    __previous_frame_button: Button
    __normal_play_dir_button: Button
    __reverse_play_dir_button: Button
    __realtime_mode_button: Button
    __custom_speed_coef_button: Button
    __custom_speed_coef_set_button: Button

    __play_speed_option_menu: OptionMenu

    __custom_speed_coef_entry: Entry

    __play_time_scale: Scale

    __actual_time_var: IntVar
    __total_time_var: IntVar
    __selected_play_speed_var: StringVar
    __custom_speed_coef_entry_var: StringVar

    def __init__(self, parent, controller: 'Controller',
                 on_change_play_state,
                 on_change_play_time,
                 on_change_play_direction,
                 on_change_play_speed,
                 on_change_play_mode,
                 on_change_frame_time):

        super().__init__(parent, borderwidth=2, bg="light grey")
        self.__controller = controller

        self.__on_change_play_state = on_change_play_state
        self.__on_change_play_time = on_change_play_time
        self.__on_change_play_direction = on_change_play_direction
        self.__on_change_play_speed = on_change_play_speed
        self.__on_change_play_mode = on_change_play_mode
        self.__on_change_frame_time = on_change_frame_time

        self.__actual_time_var = IntVar()
        self.__total_time_var = IntVar()
        self.__selected_play_speed_var = StringVar()
        self.__custom_speed_coef_entry_var = StringVar()

        self.__actual_time_var.set(0)
        self.__total_time_var.set(0)
        self.__selected_play_speed_var.set(PlaySpeed.speed_1.value[1])
        self.__custom_speed_coef_entry_var.set("0.1")

        self.__init_ui__()
        self.lock_interface()

    def __init_ui__(self) -> None:
        time_slider_frame = Frame(self)
        time_slider_frame.config(borderwidth=2, bg="light gray")

        time_control_frame = LabelFrame(self)
        time_control_frame.config(borderwidth=2, bg="light gray", text="Play controls")

        #   Time control frame
        self.__actual_time_label = Label(time_slider_frame, text="00:00.000", borderwidth=1,
                                         bg='light grey', relief='flat',
                                         width=8, height=1)
        self.__total_time_label = Label(time_slider_frame, text="00:00.000", borderwidth=1,
                                        bg='light grey', relief='flat',
                                        width=8, height=1)
        self.__play_time_scale = Scale(time_slider_frame, orient='horizontal', length=600, sliderlength=15,
                                       from_=0, to=1000, resolution=1, width=15, showvalue=False,
                                       bg="light grey",
                                       command=lambda: self.__on_change_play_time("jump",
                                                                                  self.__actual_time_var.get()),
                                       variable=self.__actual_time_var)

        #   Play control frame
        self.__play_pause_button = Button(time_control_frame, text="PLAY/PAUSE",
                                          command=self.__on_change_play_state)
        self.__go_start_button = Button(time_control_frame, text="START",
                                        command=lambda: self.__on_change_play_time("go_start"))
        self.__go_end_button = Button(time_control_frame, text="END",
                                      command=lambda: self.__on_change_play_time("go_end"))
        self.__next_frame_button = Button(time_control_frame, text="NEXT",
                                          command=lambda: self.__on_change_play_time("next_frame"))
        self.__previous_frame_button = Button(time_control_frame, text="PREVIOUS",
                                              command=lambda: self.__on_change_play_time("previous_frame"))
        self.__normal_play_dir_button = Button(time_control_frame, text="NORMAL",
                                               command=lambda: self.__on_change_play_direction("normal"))
        self.__reverse_play_dir_button = Button(time_control_frame, text="REVERSE",
                                                command=lambda: self.__on_change_play_direction("reverse"))

        #   Speed control frame
        speed_control_frame = LabelFrame(self)
        speed_control_frame.config(borderwidth=2, bg="light gray", text="Speed controls")

        self.__realtime_mode_button = Button(speed_control_frame, text="REAL-TIME",
                                             command=lambda: self.__on_change_play_mode("real-time"))
        self.__play_speed_option_menu = OptionMenu(speed_control_frame, self.__selected_play_speed_var,
                                                   *[e.value[1] for e in PlaySpeed],
                                                   command=lambda x: self.__on_change_play_speed(
                                                       [e.value[1] for e in PlaySpeed].index(x)))
        self.__custom_speed_coef_button = Button(speed_control_frame, text="CUSTOM",
                                                 command=lambda: self.__on_change_play_mode("custom"))

        self.__custom_speed_coef_entry = Entry(speed_control_frame, textvariable=self.__custom_speed_coef_entry_var)
        self.__custom_speed_coef_set_button = Button(speed_control_frame, text="SET",
                                                     command=lambda: self.__on_change_frame_time(self.__custom_speed_coef_entry_var.get()))

        #   Disposition of all elements
        self.__actual_time_label.grid(column=0, row=0, sticky='nwse', ipadx=5, padx=5, pady=5)
        self.__play_time_scale.grid(column=1, row=0, sticky='nwse', ipadx=5, padx=5, pady=5)
        self.__total_time_label.grid(column=2, row=0, sticky='nwse', ipadx=5, padx=5, pady=5)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        #   Initialize play control elements
        self.__play_pause_button.grid(row=0, column=0, rowspan=2, columnspan=1, sticky='nswe', ipadx=5, padx=5, pady=5)
        self.__go_start_button.grid(row=0, column=1, columnspan=1, sticky='nswe', ipadx=5, padx=5, pady=5)
        self.__go_end_button.grid(row=0, column=2, columnspan=1, sticky='nswe', ipadx=5, padx=5, pady=5)
        self.__next_frame_button.grid(row=1, column=2, columnspan=1, sticky='nswe', ipadx=5, padx=5, pady=5)
        self.__previous_frame_button.grid(row=1, column=1, columnspan=1, sticky='nswe', ipadx=5, padx=5, pady=5)
        self.__normal_play_dir_button.grid(row=0, column=3, columnspan=2, sticky='nswe', ipadx=5, padx=5, pady=5)
        self.__reverse_play_dir_button.grid(row=1, column=3, columnspan=2, sticky='nswe', ipadx=5, padx=5, pady=5)

        #   Initialize speed control elements
        self.__realtime_mode_button.grid(row=0, column=0, columnspan=3, sticky='nswe', ipadx=5, padx=5, pady=5)
        self.__play_speed_option_menu.grid(row=0, column=3, columnspan=3, sticky='nswe', ipadx=5, padx=5, pady=5)
        self.__custom_speed_coef_button.grid(row=1, column=0, columnspan=3, sticky='nswe', ipadx=5, padx=5, pady=5)
        self.__custom_speed_coef_entry.grid(row=1, column=3, columnspan=2, sticky='nswe', ipadx=5, padx=5, pady=5)
        self.__custom_speed_coef_set_button.grid(row=1, column=5, columnspan=1, sticky='nswe', ipadx=5, padx=5, pady=5)

        time_slider_frame.grid(row=0, column=0, columnspan=10, sticky='nwe')
        time_control_frame.grid(row=1, column=0, columnspan=3, sticky='nw')
        speed_control_frame.grid(row=1, column=3, columnspan=7, sticky='nw')

        self.lock_interface()

    def change_frame_time_entry_to_red(self):
        self.__custom_speed_coef_entry['bg'] = 'red'

    def reset_custom_time_coef_entry_color(self):
        self.__custom_speed_coef_entry['bg'] = 'white'

    def set_custom_time_coef_entry_content(self, new_content: str):
        self.__custom_speed_coef_entry_var.set(new_content)

    def lock_play_controls(self) -> None:
        lock(self.__play_pause_button)
        lock(self.__go_start_button)
        lock(self.__go_end_button)
        lock(self.__next_frame_button)
        lock(self.__previous_frame_button)
        lock(self.__normal_play_dir_button)
        lock(self.__reverse_play_dir_button)

    def unlock_play_controls(self) -> None:
        unlock(self.__play_pause_button)
        unlock(self.__go_start_button)
        unlock(self.__go_end_button)
        unlock(self.__next_frame_button)
        unlock(self.__previous_frame_button)
        unlock(self.__normal_play_dir_button)
        unlock(self.__reverse_play_dir_button)

    def lock_speed_controls(self) -> None:
        lock(self.__realtime_mode_button)
        lock(self.__play_speed_option_menu)
        lock(self.__custom_speed_coef_button)
        lock(self.__custom_speed_coef_entry)
        lock(self.__custom_speed_coef_set_button)

    def unlock_speed_controls(self) -> None:
        unlock(self.__realtime_mode_button)
        unlock(self.__play_speed_option_menu)
        unlock(self.__custom_speed_coef_button)
        unlock(self.__custom_speed_coef_entry)
        unlock(self.__custom_speed_coef_set_button)

    def lock_slider(self) -> None:
        lock(self.__play_time_scale)

    def unlock_sliders(self) -> None:
        unlock(self.__play_time_scale)

    def lock_reverse_dir_button(self) -> None:
        lock(self.__reverse_play_dir_button)

    def unlock_reverse_dir_button(self) -> None:
        unlock(self.__reverse_play_dir_button)

    def lock_normal_dir_button(self) -> None:
        lock(self.__normal_play_dir_button)

    def unlock_normal_dir_button(self) -> None:
        unlock(self.__normal_play_dir_button)

    def normal_dir_mode(self) -> None:
        lock(self.__normal_play_dir_button)
        unlock(self.__reverse_play_dir_button)

    def reverse_dir_mode(self) -> None:
        unlock(self.__normal_play_dir_button)
        lock(self.__reverse_play_dir_button)

    def lock_realtime_elements(self) -> None:
        lock(self.__realtime_mode_button)
        lock(self.__play_speed_option_menu)

    def unlock_custom_time_coef_elements(self) -> None:
        unlock(self.__custom_speed_coef_button)
        unlock(self.__custom_speed_coef_entry)
        unlock(self.__custom_speed_coef_set_button)

    def realtime_mode(self) -> None:
        lock(self.__realtime_mode_button)
        unlock(self.__play_speed_option_menu)
        unlock(self.__custom_speed_coef_button)
        lock(self.__custom_speed_coef_entry)
        lock(self.__custom_speed_coef_set_button)

    def custom_time_coef_mode(self) -> None:
        unlock(self.__realtime_mode_button)
        lock(self.__play_speed_option_menu)
        lock(self.__custom_speed_coef_button)
        unlock(self.__custom_speed_coef_entry)
        unlock(self.__custom_speed_coef_set_button)

    def lock_time_slider(self) -> None:
        lock(self.__play_time_scale)

    def unlock_time_slider(self) -> None:
        unlock(self.__play_time_scale)

    def lock_interface(self) -> None:
        self.lock_play_controls()
        self.lock_speed_controls()
        self.lock_slider()

    def update_actual_time_label(self, new_value: str) -> None:
        self.__actual_time_label['text'] = new_value

    def update_actual_time_scale(self, new_value: int) -> None:
        self.__actual_time_var.set(new_value)
        self.__play_time_scale.update()

    def update_end_time_label(self, new_value: str) -> None:
        self.__total_time_label['text'] = new_value

    def update_end_time_scale(self, new_value: int) -> None:
        self.__total_time_var.set(new_value)
        update_slider_max(self.__play_time_scale, new_value)
