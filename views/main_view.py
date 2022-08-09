"""
------------------------------------------------------------------------------------------------------------------------
    Defining main application frame

    MIT Licence

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
#   Import of basic modules
from tkinter import Frame, Toplevel, Label, Button, Radiobutton, StringVar, BooleanVar, Widget, Menu
from tkinter.constants import DISABLED, NORMAL

#   Import of custom modules
from views.control_panel_view import ControlPanel

#   In order to avoid Circular Import problems
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller import Controller

"""

    MainView

    In charge of holding views inside the window.

"""


class MainView(Frame):
    __controller: 'Controller'
    __top_section: Frame
    __top_left_widget: Widget
    __top_right_widget: Widget

    __menu_toolbox: Menu
    __file_menu_toolbox: Menu
    __generation_menu_toolbox: Menu
    __control_panel_ui: ControlPanel

    def __init__(self, parent, controller: 'Controller'):
        super().__init__(parent)
        self.__controller = controller
        self.ui_init()
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nwse')

        #   Declare menubar
        self.__menu_toolbox = Menu(self.master)
        parent.config(menu=self.__menu_toolbox)

        self.__import_menu_toolbox = None
        self.__generation_menu_toolbox = None

    def ui_init(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)

        self.__top_section = Frame(self)

        self.__top_section.columnconfigure(0, weight=1)
        self.__top_section.columnconfigure(1, weight=1)
        self.__top_section.rowconfigure(0, weight=1)

    #   To get top section (generally used to set parent of a top section children)
    def get_top_section(self) -> Frame:
        return self.__top_section

    #   To attach child element to the left top of the mainview
    def attach_top_left_widget(self, widget: Widget) -> None:
        self.__top_left_widget = widget
        self.__top_left_widget.grid(row=0, column=0, sticky='nwse')

    #   To attach child element to the right top of the mainview
    def attach_top_right_widget(self, widget: Widget) -> None:
        self.__top_right_widget = widget
        self.__top_right_widget.grid(row=0, column=1, sticky='nwse')

    #   To attach controlpanel to the mainview
    def attach_control_panel(self, control_panel: ControlPanel) -> None:
        self.__control_panel_ui = control_panel
        self.__control_panel_ui.pack(side='bottom', fill='x')

    def pack_top_section(self):
        self.__top_section.pack(side='top', fill='both', expand=True)

    def set_import_menu(self, name: str, menu: Menu):
        self.__import_menu_toolbox = menu
        self.__import_menu_toolbox.master = self.__menu_toolbox
        self.__menu_toolbox.add_cascade(label=name, menu=menu)

    def set_generation_menu(self, name: str, menu: Menu):
        self.__generation_menu_toolbox = menu
        self.__generation_menu_toolbox.master = self.__menu_toolbox
        self.__menu_toolbox.add_cascade(label=name, menu=menu, state=DISABLED)

    def get_file_menu(self) -> Menu:
        return self.__file_menu_toolbox

    def get_generation_menu(self) -> Menu:
        return self.__generation_menu_toolbox

    #
    #   For the two following functions there is an unclean approach
    #   I can't do it with another approach, it is a limitation of Tkinter
    #   To change state of a menu, Tkinter need his name
    #
    def lock_generation_menu(self) -> None:
        self.__menu_toolbox.entryconfig("Generate", state=DISABLED)

    def unlock_generation_menu(self) -> None:
        self.__menu_toolbox.entryconfig("Generate", state=NORMAL)


    #   If the dataimportmodule did not detect delimiters, application will ask for delimiter setting
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

    def on_exit(self):
        self.__controller.on_exit()
