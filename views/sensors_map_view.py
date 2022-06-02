"""
------------------------------------------------------------------------------------------------------------------------
    Defining sensor map frame

    MIT Licence

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
import math
from tkinter import Canvas
from tkinter.font import Font

from position import Position

#   In order to avoid Circular Import problems
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller import Controller

"""

    SensorsMapView

    In charge of displaying classic visualisation with auto scaling

"""


class SensorsMapView(Canvas):

    __controller: 'Controller'
    __scale_factor: float
    __cache_sensors_positions: [[(int, int)]]
    __cache_c_o_m_positions: [(int, int)]
    __com_font: Font
    __sensor_name_font: Font
    __svg_bg_path: str
    __map_width: int
    __map_height: int
    __map_offset: int
    __square_height: int
    __square_width: int
    __offset_height: float
    __offset_width: float
    __y_axis_inversion: bool

    def __init__(self, parent, controller: 'Controller'):
        super().__init__(parent, borderwidth=2, bg="white")
        self.__controller = controller
        self.__com_font = Font(family='arial', size=20, weight='bold')
        self.__sensor_name_font = Font(family='arial', size=10, weight='bold')
        self.__scale_factor = 1
        self.__map_width = 0
        self.__map_height = 0
        self.__offset_height: float
        self.__offset_width: float
        self.y_axis_inversion = True

    def update_map_settings(self, height: int, width: int,
                            y_axis_inversion: bool) -> None:

        self.__map_width = width
        self.__map_height = height
        self.__y_axis_inversion = y_axis_inversion

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

    """


            CANVAS DRAWING AND DRAWING UPDATE SECTION

    """

    def draw_bg(self, drawing_data: [[[int, int]]]) -> None:
        for poly in drawing_data:
            pts: [[int, int]] = [[int(p[0] * self.__scale_factor), int(p[1] * self.__scale_factor)] for p in poly]
            self.create_polygon(pts, fill="silver", tags='bg')

    def draw_sensor(self, index: int, color: str, id: str) -> None:
        self.create_polygon(self.__cache_sensors_positions[index], fill=color, tags=id)

    def draw_sensor_names(self, position: [[int, int]], sensors_name: [str]) -> None:
        for index in range (len(sensors_name)):
            self.create_text(position[index].x * self.__scale_factor,
                             position[index].y * self.__scale_factor,
                             font=self.__sensor_name_font,
                             fill='white',
                             text=sensors_name[index])

    def update_sensor(self, color: str, id: str) -> None:
        self.itemconfigure(id, fill=color)

    def draw_center_of_mass(self, index: int) -> None:
        self.delete('com')
        self.create_text(self.__cache_c_o_m_positions[index], font=self.__com_font, tags='com', text='+')

    """


            CANVAS LISTENER SECTION

    """

    def on_resize(self) -> None:
        self.update_scale_factor()
        self.update_cache_position()
        self.delete('all')

    """


            CACHE GENERATION SECTION

    """

    def __calculate_cache_position(self, positions: [Position],
                                   sensors_characteristics: [int, int, int]) -> [[[int, int]]]:
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

    def __calculate_cache_c_o_m_position(self, positions: [Position]) -> [[int, int]]:
        new_cache: [[int, int]] = list(list())

        print("RECALCULATE C_O_M CACHE")

        for i in range(len(positions)):

            #   Scale initial position
            scaled_x = positions[i].x * self.__scale_factor

            #   Need y-axis inversion ?
            if self.__y_axis_inversion:
                scaled_y = (self.__map_height - positions[i].y) * self.__scale_factor
            else:
                scaled_y = positions[i].y * self.__scale_factor

            #   Initialize sensor array
            new_cache.append([scaled_x, scaled_y])

        return new_cache

    def update_cache_position(self):
        self.__cache_sensors_positions = self.__calculate_cache_position(self.__controller.get_dataset().get_positions(),
                                                                         self.__controller.get_dataset().get_sensors_characteristics())
        self.__cache_c_o_m_positions = self.__calculate_cache_c_o_m_position(self.__controller.get_dataset().get_c_o_m_positions())
