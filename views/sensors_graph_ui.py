"""
------------------------------------------------------------------------------------------------------------------------
    Defining sensor graph frame

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
import time
from tkinter import Canvas

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.ndimage import *

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

    #
    def points_to_gaussian_heatmap(self, centers, height, width):

        start_time = time.time()
        # create a grid of (x,y) coordinates at which to evaluate the kernels
        a = np.empty((width, height))

        a_ = time.time()-start_time
        start_time = time.time()

        for x_, y_, z_ in centers:
            a[x_, y_]: int = z_

        b_ = time.time()-start_time
        start_time = time.time()

        img = gaussian_filter(a, sigma=30, mode='nearest', cval=5)
        c_ = time.time()-start_time

        print(a_)
        print(b_)
        print(c_)

        print(a_ + b_ + c_)

        return img

    def plot(self):
        # the figure that will contain the plot
        start_time = time.time()

        img = self.points_to_gaussian_heatmap([(50, 50, 0.5), (75, 75, 0.5), (50, 250, 0.1), (250, 250, 1)],
                                              300, 600)
        fig = plt.figure(figsize=(2, 4), dpi=128)
        plt.imshow(img, cmap='jet')
        plt.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=0)
        print(time.time()-start_time)

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
