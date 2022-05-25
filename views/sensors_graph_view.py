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

import numpy as np
from cv2 import GaussianBlur, BORDER_REPLICATE
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from position import Position
from utils import a_or_b_in_bounds

#   In order to avoid Circular Import problems
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller import Controller


class SensorsGraphView(Canvas):

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

    #   CONSTANTS
    __GAUSS_KERN_SIZE = 61
    __SIGMA = 16
    __MAX_VALUE_AFTER_GAUSS = 6.229835807198149e-4
    __MIN_VALUE_ACCEPTED = 1.2e-4

    def __init__(self, parent, controller: 'Controller'):
        super().__init__(parent, borderwidth=2, bg="white")
        self.__controller = controller
        self.__scale_factor = 1
        self.__graph_width = 0
        self.__graph_height = 0

        #   Will scan neighbourhood and return neighbouring matrices
    def find_neighbouring_matrices(self,
                                   origin_matrix_bounds: list[[int, int], [int, int]],
                                   matrices_id_array: list[int],
                                   matrices_bounds_array: [[[int, int], [int, int]]]) -> [int]:

        if not (0 < len(matrices_bounds_array) and 0 < len(matrices_id_array) and len(matrices_bounds_array) == len(matrices_id_array)):
            raise Exception("Number of matrices id and matrices centers must be equal and both above zero !")

        neighbouring_matrices_id = list()
        neighbouring_matrices_bounds = list()

        nb_of_matrices = len(matrices_id_array)

        tmp_1 = matrices_id_array.copy()
        tmp_2 = matrices_bounds_array.copy()

        for index in range (nb_of_matrices - 1, -1, -1):
            if a_or_b_in_bounds(*matrices_bounds_array[index][0],
                                *origin_matrix_bounds[0]) and a_or_b_in_bounds(*matrices_bounds_array[index][1],
                                                                               *origin_matrix_bounds[1]):
                neighbouring_matrices_id.append(matrices_id_array[index])
                neighbouring_matrices_bounds.append(matrices_bounds_array[index])
                tmp_1.pop(index)
                tmp_2.pop(index)

        if len(tmp_1) > 0 or len(tmp_2) > 0:
            nb_of_nb_matrices = len(neighbouring_matrices_id)

            for index in range(0, nb_of_nb_matrices - 1):
                if len(tmp_1) > 0 or len(tmp_2) > 0:
                    result = self.find_neighbouring_matrices(neighbouring_matrices_bounds[index], tmp_1, tmp_2)
                    if len(result) > 0:
                        neighbouring_matrices_id += result

        return neighbouring_matrices_id

    def cut_to_matrix_groups(self, centers: [[int, int]],
                             kern_x_bounds: [[int, int]],
                             kern_y_bounds: [[int, int]]) -> [[int]]:

        if not(len(centers) > 0):
            raise Exception("Number of centers must be above zero !")

        nb_of_points = len(centers)

        bounds: [[[int, int], [int, int]]] = [[kern_x_bounds[i], kern_y_bounds[i]] for i in range(0, nb_of_points)]
        tested_points: [int] = [i for i in range(0, nb_of_points)]

        result_list = list()

        while len(tested_points) > 0:

            tmp = self.find_neighbouring_matrices(bounds[tested_points[0]],
                                                  [x for x in tested_points],
                                                  [bounds[x] for x in tested_points])
            tested_points = list(set(tested_points) - set(tmp))
            result_list.append(tmp)

        return result_list

    def create_matrix_from_groups(self, centers: [[int, int]],
                                  kern_x_bounds: [[int, int]],
                                  kern_y_bounds: [[int, int]],
                                  sensors_values: [float],
                                  mtx_grps: [[int]]) -> [[[float]]]:

        generated_matrices: [([int, int], [int])] = list()

        for grp in mtx_grps:

            kern_grp_x_bounds = [kern_x_bounds[i] for i in grp]
            kern_grp_y_bounds = [kern_y_bounds[i] for i in grp]

            min_x: int = np.min(kern_grp_x_bounds)
            max_x: int = np.max(kern_grp_x_bounds)

            min_y: int = np.min(kern_grp_y_bounds)
            max_y: int = np.max(kern_grp_y_bounds)

            height = max_y - min_y
            width = max_x - min_x

            matrix = np.zeros((width, height), dtype=float)

            for x in grp:
                matrix[centers[x][0] - min_x][centers[x][1] - min_y] = sensors_values[x]

            generated_matrices.append(([min_x, min_y], matrix))

        return generated_matrices

    #
    #   Recommended settings
    #       sigma = 16      low_cut = 1.2e-4        kern_size = (61, 61)
    #
    def gaussian_heatmap_filter(self, matrix: np.array,
                                kern_width: int,kern_height: int,
                                sigma: float, low_cut: float):

        start_time = time.time()

        #   Apply gaussian filter of OpenCV to our matrix
        img = GaussianBlur(matrix,
                           (kern_width, kern_height),
                           borderType=BORDER_REPLICATE,
                           sigmaX=sigma,
                           sigmaY=sigma)

        #   Cut the low part that doesn't interest us
        img[img < low_cut] = 0
        
        print(time.time()-start_time)

        return img

    def plot(self):
        # the figure that will contain the plot
        start_time = time.time()

        xy = [[100, 100], [150, 150], [200, 200], [150, 500]]
        size = (300, 600)

        kern_half = self.__GAUSS_KERN_SIZE // 2
        kern_x = [[x - kern_half, x + kern_half + 1] for x, _ in xy]
        kern_y = [[y - kern_half, y + kern_half + 1] for _, y in xy]

        t = self.cut_to_matrix_groups(xy, kern_x, kern_y)
        ta = self.create_matrix_from_groups(xy, kern_x, kern_y, [1, 0.75, 0.5, 0.25], t)

        print(time.time()-start_time)

        palette = copy(plt.get_cmap('jet'))
        palette.set_under('white', 0)

        result = np.zeros(size, dtype=float)

        print(time.time() - start_time)
        print("####")
        start_time = time.time()

        for x, a in ta:
            img = self.gaussian_heatmap_filter(a,
                                               self.__GAUSS_KERN_SIZE,
                                               self.__GAUSS_KERN_SIZE,
                                               self.__SIGMA,
                                               self.__MIN_VALUE_ACCEPTED)
            c, r = x
            result[c:c + a.shape[0], r:r + a.shape[1]] = img
            print(time.time() - start_time)
            start_time = time.time()
            print("####")

            # img = np.asarray([[get_color_gradient_graph(i) for i in x] for x in img], dtype=np.uint8)

        fig = plt.figure(figsize=(1, 5), dpi=512)

        plt.imshow(result, cmap=palette)

        plt.clim(vmin=1.22e-4, vmax=self.__MAX_VALUE_AFTER_GAUSS)
        plt.autoscale(True)

        plt.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=1)

        print(time.time()-start_time)


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
                scaled_y = (self.__graph_height - positions[i].y) * self.__scale_factor
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
        if self.__graph_height <= 0 or self.__graph_width <= 0 or canvas_height <= 0 or canvas_width <= 0:
            return False

        x_scale_factor: float = canvas_width / self.__graph_width
        y_scale_factor: float = canvas_height / self.__graph_height

        #   Select the best-fit scale factor
        #   Scaled map height and width mus fit in the frame height and width
        #   Calculate difference between canvas side and scale side, a good factor
        #   have a positive or null difference, null will be perfect, a bad factor
        #   have a negative difference
        x_diff = canvas_width - (y_scale_factor * self.__graph_width)
        y_diff = canvas_height - (x_scale_factor * self.__graph_height)

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
