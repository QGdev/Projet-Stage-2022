"""
------------------------------------------------------------------------------------------------------------------------
    Defining the pop up that will allow the user to modify configuration

    BUT UNIMPLEMENTED FOR NOW

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
from tkinter import Toplevel

from dataset import DataSet


class ModifyConfigPopUp(Toplevel):

    __on_confirm: 'function'
    __on_cancel: 'function'

    def __init__(self, parent, on_confirm, on_cancel):
        super().__init__(parent)
        self.wm_title("Modify configuration")
        self.resizable(False, False)
        pass

    def show(self, dataset: DataSet):
        pass
