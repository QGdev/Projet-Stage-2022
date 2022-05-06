"""
------------------------------------------------------------------------------------------------------------------------
    Defining sensor graph frame

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""

from tkinter import Tk, Frame, Menu, filedialog, Canvas, Label

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.ndimage.filters import gaussian_filter

from position import Position


class SensorsGraphUI(Canvas):
    __controller: 'Controller'
    __scale_factor: float
    __cache: [[Position]]
    __map_width: int
    __map_height: int
    __map_offset: int
    __square_height: int
    __square_width: int
    __offset_height: float
    __offset_width: float

    def __init__(self, parent, controller: 'Controller'):
        super().__init__(parent, borderwidth=2, bg="white")
        self.__controller = controller
        self.__scale_factor = 1
        self.__map_width = 0
        self.__map_height = 0
        self.__map_offset = 5
        self.__offset_height = 0.0
        self.__offset_width = 0.0

    def plot(self):
        # the figure that will contain the plot
        fig = Figure(figsize=(5, 7),
                     dpi=75)

        """def heatmap2d(arr: np.ndarray):
            plt.imshow(arr, cmap='viridis')
            plt.colorbar()
            plt.show()"""


        b, a = np.meshgrid(np.linspace(-1, 1, 130), np.linspace(-1, 1, 130))
        b = gaussian_filter(b, sigma=8)

        c = (a ** 2 + b ** 2) * np.exp(-a ** 2 - b ** 2)
        c = c[:-1, :-1]
        l_a = a.min()
        r_a = a.max()
        l_b = b.min()
        r_b = b.max()
        l_c, r_c = -np.abs(c).max(), np.abs(c).max()

        figure, axes = plt.subplots()

        c = axes.pcolormesh(a, b, c, cmap='brg', vmin=l_c, vmax=r_c)
        axes.set_title('Heatmap')
        axes.axis([l_a, r_a, l_b, r_b])
        figure.colorbar(c)

        # adding the subplot
        #plot1 = fig.add_subplot()

        # plotting the graph
        #plot1.plot(c)

        # creating the Tkinter canvas
        # containing the Matplotlib figure
        #canvas = FigureCanvasTkAgg(figure, master=self)
        #canvas.draw()

        # placing the canvas on the Tkinter window
        #canvas.get_tk_widget().pack()

    def update_map_settings(self, height: int, width: int, square_height: int, square_width: int) -> None:

        self.__map_width = width
        self.__map_height = height
        self.__square_width = square_width + self.__map_offset
        self.__square_height = square_height + self.__map_offset
        self.__map_offset = max(square_height, square_width) // 2

        self.__offset_width = (square_height / 2) + self.__map_offset
        self.__offset_height = (square_height / 2) + self.__map_offset

        self.__offset_width += self.__map_offset * 2
        self.__offset_height += self.__map_offset * 2

    def on_resize(self) -> None:
        self.update_scale_factor()
        self.update_cache()
        self.delete('all')
        self.update()

    def __calculate_cache(self):
        positions: [Position] = self.__controller.get_dataset().get_positions()
        new_cache: [[Position]] = []

        scaled_width = self.__square_width * self.__scale_factor
        scaled_height = self.__square_height * self.__scale_factor

        for pos in positions:
            scaled_x = (pos.x + self.__map_offset) * self.__scale_factor
            scaled_y = (self.__map_height - pos.y - self.__map_offset) * self.__scale_factor

            new_cache.append([Position(scaled_x - scaled_width, scaled_y - scaled_height),
                              Position(scaled_x + scaled_width, scaled_y + scaled_height)])

        return new_cache

    def update_cache(self):
        self.__cache = self.__calculate_cache()

    def update_scale_factor(self):
        #   Importation of used parameters to avoid long annoying code
        #       For canvas size parameters
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        #   Avoid the fatal zero division
        if self.__map_height <= 0 or self.__map_width <= 0 or canvas_height <= 0 or canvas_width <= 0:
            return False

        x_scale_factor: float = canvas_width / self.__map_width
        y_scale_factor: float = canvas_height / self.__map_height

        #   Select the best-fit scale factor
        #   Scaled map height and width mus fit in the frame height and width
        #   Calculate difference between canvas side and scale side, a good factor
        #   have a positive or null difference, null will be perfect, a bad factor
        #   have a negative difference
        x_diff = canvas_width - (y_scale_factor * self.__map_width)
        y_diff = canvas_height - (x_scale_factor * self.__map_height)

        #   Both factors are bad ones (this should not normally happen).
        if x_diff < 0 and y_diff < 0:
            return False

        #   We will only take the greatest between those both
        if 0 <= x_diff <= y_diff or y_diff < 0 <= x_diff:
            self.__scale_factor = y_scale_factor
        elif 0 <= y_diff < x_diff or x_diff < 0 <= y_diff:
            self.__scale_factor = x_scale_factor
        else:
            self.__scale_factor = 1
            return False
        return True
