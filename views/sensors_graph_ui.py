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
from sys import getsizeof
from tkinter import Canvas

import cv2
import numpy as np
import scipy.stats
from cv2 import BORDER_REPLICATE
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import sparse
from scipy.ndimage import gaussian_filter

from position import Position


class SensorsGraphUI(Canvas):
    __controller: 'Controller'
    __scale_factor: float
    __cache_sensors_positions: [[(int, int)]]
    __graph_width: int
    __graph_height: int

    __graph_gen_width: int
    __graph_gen_height: int

    __kern_width: int
    __kern_height: int

    __y_axis_inversion: bool

    def __init__(self, parent, controller: 'Controller'):
        super().__init__(parent, borderwidth=2, bg="white")
        self.__controller = controller
        self.__scale_factor = 1
        self.__graph_width = 0
        self.__graph_height = 0

    #
    #   Only tests for now !
    #
    def points_to_gaussian_heatmap(self, centers: [int, int], sensors_values: [int], width, height):

        if len(centers) != len(sensors_values):
            raise Exception("Number of sensors positions must be the same as the number of sensors values !")

        start_time = time.time()
        # create a grid of (x,y) coordinates at which to evaluate the kernels
        a = np.empty((height, width))

        a_ = time.time()-start_time
        start_time = time.time()

        for i in range(len(centers)):
            a[int((centers[i][1]) * 0.7 + 0.15 * height),
              int((width - centers[i][0]) * 0.7 + 0.15 * width)] = float(sensors_values[i])

        b_ = time.time()-start_time
        start_time = time.time()

        img = cv2.GaussianBlur(a, (61, 61), borderType=BORDER_REPLICATE, sigmaX=16, sigmaY=16)

        img[img < 1.2e-4] = 0

        c_ = time.time()-start_time

        print(a_)
        print(b_)
        print(c_)

        print(a_ + b_ + c_)

        return img

    def plot(self):
        # the figure that will contain the plot
        start_time = time.time()

        img = self.points_to_gaussian_heatmap([[140, 550], [85, 165], [185, 150], [285, 110]],
                                              [1, 1, 1, 1],
                                              325, 650)
        """

        fig = plt.figure(figsize=(1, 5), dpi=256)

        palette = copy(plt.get_cmap('jet'))
        palette.set_under('white', 0)

        plt.imshow(img, cmap=palette)
        plt.clim(vmin=1.2e-4, vmax=6.229835807198149e-4)
        plt.autoscale(True)

        plt.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=1)

        print(time.time()-start_time)
        print(getsizeof(img))
        print(img)
        x = scipy.sparse.csc_matrix(img)
        print(x)
        a = scipy.sparse.csr_matrix(img)
        print(getsizeof(a))
        print(a)
        b = scipy.sparse.dok_matrix(img)
        print(getsizeof(b))
        print(b)
        c = scipy.sparse.bsr_matrix(img)
        print(getsizeof(c))
        print(c)
        d = scipy.sparse.coo_matrix(img)
        print(getsizeof(d))
        print(d)
        pass
        """

    def update_graph_settings(self, height: int, width: int,
                                y_axis_inversion: bool) -> None:
        self.__graph_width = width
        self.__graph_height = height
        self.__y_axis_inversion = y_axis_inversion

    def on_resize(self) -> None:
        self.update_scale_factor()
        self.update_cache_position()
        self.delete('all')
        self.update()

    def draw_bg(self, drawing_data: [[[int, int]]]) -> None:
        for poly in drawing_data:
            self.create_polygon([[int(p[0] * self.__scale_factor), int(p[1] * self.__scale_factor)] for p in poly],
                                stipple='gray75', fill="grey", tags='bg')

    def draw_sensor(self, index: int, color: str) -> None:
        self.create_polygon(self.__cache_position[index], fill=color, tags='sensor')

    def __calculate_cache_position(self):
        positions: [Position] = self.__controller.get_dataset().get_positions()
        sensors_characteristics: [int, int, int] = self.__controller.get_dataset().get_sensors_characteristics()
        new_cache: [[[int, int]]] = list(list())

        print("RECALCULATE CACHE")

        for i in range(len(positions)):

            #   Scale sensor dimensions
            scaled_width = sensors_characteristics[i][0] * self.__scale_factor
            scaled_height = sensors_characteristics[i][1] * self.__scale_factor

            #   Scale initial position
            scaled_x = positions[i].x * self.__scale_factor

            #   Need y-axis inversion ?
            if self.__y_axis_inversion:
                scaled_y = (self.__map_height - positions[i].y) * self.__scale_factor
            else:
                scaled_y = positions[i].y * self.__scale_factor

            #   Calculate other points needed and cos and sin values to avoid repetitive calculation in the next part
            s_x_1 = scaled_x + scaled_width
            s_y_1 = scaled_y + scaled_height

            alpha = math.radians(sensors_characteristics[i][2])
            cos_alpha = math.cos(alpha)
            sin_alpha = math.sin(alpha)

            #   Initialize sensor array
            new_cache.append([])

            #   Add each coordinates points
            #   A -- B
            #   |    |
            #   D -- C
            #
            #   A
            new_cache[i].append([int(scaled_x * cos_alpha - scaled_y * sin_alpha),
                                 int(scaled_x * sin_alpha + scaled_y * cos_alpha)])
            #   B
            new_cache[i].append([int(s_x_1 * cos_alpha - scaled_y * sin_alpha),
                                 int(s_x_1 * sin_alpha + scaled_y * cos_alpha)])
            #   C
            new_cache[i].append([int(s_x_1 * cos_alpha - s_y_1 * sin_alpha),
                                 int(s_x_1 * sin_alpha + s_y_1 * cos_alpha)])
            #   D
            new_cache[i].append([int(scaled_x * cos_alpha - s_y_1 * sin_alpha),
                                 int(scaled_x * sin_alpha + s_y_1 * cos_alpha)])

            #   For debugging purposes
            #   print(i)
            #   print(new_cache[i])
        return new_cache

    def update_cache_position(self):
        self.__cache_position = self.__calculate_cache_position()

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
