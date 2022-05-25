"""
------------------------------------------------------------------------------------------------------------------------
    Defining main application frame

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
from tkinter import Frame, Toplevel, Label, Button, Radiobutton, StringVar, BooleanVar, Widget
from tkinter import filedialog as fd

from views.control_panel_view import ControlPanel

#   In order to avoid Circular Import problems
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller import Controller


class MainView(Frame):
    __controller: 'Controller'
    __top_section: Frame
    __top_left_widget: Widget
    __top_right_widget: Widget
    __control_panel_ui: ControlPanel

    def __init__(self, parent, controller: 'Controller'):
        super().__init__(parent)
        self.__controller = controller
        self.ui_init()
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nwse')

    def ui_init(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)

        self.__top_section = Frame(self)

        self.__top_section.columnconfigure(0, weight=1)
        self.__top_section.columnconfigure(1, weight=1)
        self.__top_section.rowconfigure(0, weight=1)

    def get_top_section(self) -> Frame:
        return self.__top_section

    def attach_top_left_widget(self, widget: Widget) -> None:
        self.__top_left_widget = widget
        self.__top_left_widget.grid(row=0, column=0, sticky='nwse')

    def attach_top_right_widget(self, widget: Widget) -> None:
        self.__top_right_widget = widget
        self.__top_right_widget.grid(row=0, column=1, sticky='nwse')

    def attach_control_panel(self, control_panel: ControlPanel) -> None:
        self.__control_panel_ui = control_panel
        self.__control_panel_ui.pack(side='bottom', fill='x')

    def pack_top_section(self):
        self.__top_section.pack(side='top', fill='both', expand=True)


    def ask_for_csv_settings(self, possible_delimiters: [(str, str)]):
        pop_up = Toplevel(self)
        pop_up.wm_title("CSV settings")
        pop_up.resizable(False, False)

        Label(pop_up, text="Cannot detect settings for the provided CSV file").pack(padx=20, pady=20, fill='x')

        selected = StringVar()
        selected.set(possible_delimiters[0][1])

        for i in range(0, len(possible_delimiters)):
            Radiobutton(pop_up, variable=selected, value=possible_delimiters[i][1], text=possible_delimiters[i][0]) \
                .pack(padx=20, pady=2)

        button_has_been_pressed = BooleanVar()
        button_has_been_pressed.set(False)

        button = Button(pop_up, text="Next", command=lambda: button_has_been_pressed.set(True))
        button.pack(padx=20, pady=5, fill='x')

        button.wait_variable(button_has_been_pressed)
        pop_up.destroy()
        return selected.get()

    def on_import(self):
        filename = fd.askopenfilename(
            title='Open a data file',
            initialdir='~/',
            filetypes=(("CSV Files", ".csv"),))

        #   The user didn't select anything or just close the dialog
        #   So we just abort the function
        if filename == "" or filename == "()":
            return

        self.__controller.load_data_full_csv(filename)

    def on_exit(self):
        self.__controller.on_exit()
