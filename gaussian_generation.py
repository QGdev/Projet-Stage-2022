"""
------------------------------------------------------------------------------------------------------------------------
    Defining functions and methods that will be used to generate gaussian map

    MIT Licence

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
from copy import copy
from typing import IO

import numpy as np
from cv2 import GaussianBlur, BORDER_REPLICATE

from views.sensors_graph_view import *
from utils import *
import time

__GAUSS_KERN_SIZE = 121
__SIGMA = 16
__MAX_VALUE_AFTER_GAUSS = 0.0006218925859372295
__MIN_VALUE_ACCEPTED = 1e-6


#   Will scan neighbourhood and return neighbouring matrices
def find_neighbouring_matrices(origin_matrix_bounds: list[[int, int], [int, int]],
                               matrices_id_array: list[int],
                               matrices_bounds_array: [[[int, int], [int, int]]]) -> [int]:
    if not (0 < len(matrices_bounds_array) and 0 < len(matrices_id_array) and len(matrices_bounds_array) == len(
            matrices_id_array)):
        raise Exception("Number of matrices id and matrices centers must be equal and both above zero !")

    neighbouring_matrices_id = list()
    neighbouring_matrices_bounds = list()

    nb_of_matrices = len(matrices_id_array)

    tmp_1 = matrices_id_array.copy()
    tmp_2 = matrices_bounds_array.copy()

    for index in range(nb_of_matrices - 1, -1, -1):
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
                result = find_neighbouring_matrices(neighbouring_matrices_bounds[index], tmp_1, tmp_2)
                if len(result) > 0:
                    neighbouring_matrices_id += result

    return neighbouring_matrices_id


def cut_to_matrix_groups(centers: [Position],
                         kern_x_bounds: [[int, int]],
                         kern_y_bounds: [[int, int]]) -> [[int]]:
    if not (len(centers) > 0):
        raise Exception("Number of centers must be above zero !")

    nb_of_points = len(centers)

    bounds: [[[int, int], [int, int]]] = [[kern_x_bounds[i], kern_y_bounds[i]] for i in range(0, nb_of_points)]
    tested_points: [int] = [i for i in range(0, nb_of_points)]

    result_list = list()

    while len(tested_points) > 0:
        tmp = find_neighbouring_matrices(bounds[tested_points[0]],
                                         [x for x in tested_points],
                                         [bounds[x] for x in tested_points])
        tested_points = list(set(tested_points) - set(tmp))
        result_list.append(tmp)

    return result_list


def create_matrix_from_groups(centers: [Position],
                              kern_x_bounds: [[int, int]],
                              kern_y_bounds: [[int, int]],
                              sensors_values: [float],
                              mtx_grps: [[int]]) -> [([int, int], [[float]])]:
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

        matrix = np.zeros((height, width), dtype=float)

        for x in grp:
            matrix[centers[x].y - min_y][centers[x].x - min_x] = sensors_values[x]

        generated_matrices.append(([min_x, min_y], matrix))

    return generated_matrices


def gaussian_heatmap_filter(m: np.array,
                            kern_width: int, kern_height: int,
                            sigma: float, low_cut: float):
    start_time = time.time()
    #   Apply gaussian filter of OpenCV to our matrix
    img = GaussianBlur(m,
                       (kern_width, kern_height),
                       borderType=BORDER_REPLICATE,
                       sigmaX=sigma,
                       sigmaY=sigma)

    #   Cut the low part that doesn't interest us
    img[img < low_cut] = 0

    print(time.time() - start_time)

    return img


def generate_save_image(sensors_pos: [[int, int]], sensors_values: [float], map_size: (int, int),
                        save_loc: IO) -> None:

    #   Y X
    size = (map_size[1], map_size[0])

    kern_half = __GAUSS_KERN_SIZE // 2
    kern_x = [[p.x - kern_half, p.x + kern_half + 1] for p in sensors_pos]
    kern_y = [[p.y - kern_half, p.y + kern_half + 1] for p in sensors_pos]

    ta = create_matrix_from_groups(sensors_pos, kern_x, kern_y, sensors_values,
                                   cut_to_matrix_groups(sensors_pos, kern_x, kern_y))

    result = np.zeros(size, dtype=float)

    #   Generate each kern matrices points and reassemble the whole matrix
    for x, a in ta:
        #   Generation
        img = gaussian_heatmap_filter(a,
                                      __GAUSS_KERN_SIZE,
                                      __GAUSS_KERN_SIZE,
                                      __SIGMA,
                                      __MIN_VALUE_ACCEPTED)
        #   Reassembly
        c, r = x
        result[r:r + a.shape[0], c:c + a.shape[1]] = img

    #   print(np.max(result))

    palette = copy(plt.get_cmap('jet'))
    palette.set_under('white', __MIN_VALUE_ACCEPTED)

    #   Generate figure and save it into an image
    plt.autoscale(enable=True, axis='both', tight=True)

    plt.axis('off')
    plt.imsave(save_loc, result,
               cmap=palette, format="jpg", dpi=512,
               vmin=__MIN_VALUE_ACCEPTED, vmax=__MAX_VALUE_AFTER_GAUSS)
    plt.axis('on')
