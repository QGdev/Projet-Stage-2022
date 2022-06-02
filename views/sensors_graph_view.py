"""
------------------------------------------------------------------------------------------------------------------------
    Defining sensor graph frame

    MIT Licence

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
#   Import of basic modules
from tkinter import Canvas
from tkinter.constants import BOTH
from matplotlib import pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#   In order to avoid Circular Import problems
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller import Controller

"""

    SensorsGraphView

    Just show a view with graph drawing with matplotlib

"""


class SensorsGraphView(Canvas):

    __controller: 'Controller'

    def __init__(self,
                 parent,
                 controller: 'Controller'):
        super().__init__(parent, borderwidth=2, bg="white")
        self.__controller = controller

    #   Call it once to draw a graph
    def plot(self,
             sensor_data: [[float]],
             sensors_names: [str],
             temporal_set: [float]):

        fig, ax = plt.subplots()

        #   Set labels for each axis
        ax.set_xlabel('time (s)')
        ax.set_ylabel('sensors_values')

        #   Draw each sensors data
        for data in sensor_data:
            ax.plot(temporal_set, data)

        #   Put legends
        ax.legend(sensors_names)

        ax.margins(x=0.02, y=0.02)
        ax.tick_params(axis='both')

        plt.autoscale(enable=True, axis='both', tight=False)

        canvas = FigureCanvasTkAgg(fig, master=self)
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10,
                                    pady=10,
                                    fill=BOTH,
                                    expand=True)

    #   Used to clear the view
    def clear(self):
        for widgets in self.winfo_children():
            widgets.destroy()
