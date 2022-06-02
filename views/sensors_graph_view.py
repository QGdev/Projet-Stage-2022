"""
------------------------------------------------------------------------------------------------------------------------
    Defining sensor graph frame

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
import math
import time
from copy import copy
from tkinter import Canvas
from tkinter.constants import BOTH

import numpy as np
from cv2 import GaussianBlur, BORDER_REPLICATE
from matplotlib import pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from gaussian_generation import create_matrix_from_groups, cut_to_matrix_groups
from position import Position
from utils import a_or_b_in_bounds

#   In order to avoid Circular Import problems
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller import Controller


class SensorsGraphView(Canvas):

    __controller: 'Controller'
    __sensors_values: [[float]]

    def __init__(self, parent, controller: 'Controller'):
        super().__init__(parent, borderwidth=2, bg="white")
        self.__controller = controller
        self.__sensors_values = list()

    def plot(self, sensor_data: [[float]], sensors_names: [str], temporal_set:[float]):
        # the figure that will contain the plot
        start_time = time.time()

        fig, ax = plt.subplots()
        ax.set_xlabel('time (s)')
        ax.set_ylabel('sensors_values')

        for data in sensor_data:
            ax.plot(temporal_set, data)

        ax.legend(sensors_names)
        ax.margins(x=0.02, y=0.02)
        ax.tick_params(axis='y')

        plt.autoscale(enable=True, axis='both', tight=False)

        canvas = FigureCanvasTkAgg(fig, master=self)
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        print(time.time() - start_time)

    def clear(self):
        for widgets in self.winfo_children():
            widgets.destroy()