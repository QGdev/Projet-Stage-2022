"""
------------------------------------------------------------------------------------------------------------------------
    Defining functions and methods used in order to get data from a csv file

    MIT Licence

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
#   Import of basic modules
import math
import re as regexp
from tkinter import Scale, Button, OptionMenu, Entry, Menu
from tkinter.constants import DISABLED, NORMAL
from tkinter.ttk import Widget

#   Import of custom modules
from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier, Move, Close
from position import Position

"""

    Utils

    Used as a huge container for generic functions that is or can be used somewhere else

"""


#   In order to get a file
def get_file(file_path: str, encoding: str = "ISO-8859-1"):
    return open(file_path, newline='', encoding=encoding)


#   Used to detect difference between a simple string and a string containing an int value
def is_a_int_value(value: str) -> bool:
    #   Check the string with some regex
    return regexp.match("^-?[0-9]+$", value) is not None


#   Used to detect difference between a simple string and a string containing a float or int value
def is_a_numerical_value(value: str) -> bool:
    #   Check the string with some regex
    return regexp.match("^-?[0-9]+((.|,)[0-9]+)?$", value) is not None


#   Used to extract float or int value
#   Will return None if no value was found
def extract_numerical_value(value: str) -> float | int | None:
    #   Extract value from string
    regexp_extracted = regexp.search("-?[0-9]+((.|,)[0-9]+)?", value)

    #   Check if the regexp found something else we quit
    if regexp_extracted is None:
        return None

    resulted_str = regexp_extracted.string[regexp_extracted.regs[0][0]:regexp_extracted.regs[0][1]]

    #   Check if the resulted string is a numerical value
    if not is_a_numerical_value(resulted_str):
        return None

    #   Convert string to numerical value
    if is_a_int_value(resulted_str):
        return int(resulted_str)

    return float(resulted_str)


#   Used to extract positive float or int value
#   Will return None if no value was found
def extract_positive_numerical_value(value: str) -> float | int | None:
    #   Extract value from string
    regexp_extracted = regexp.search("[0-9]+((.|,)[0-9]+)?", value)

    #   Check if the regexp found something else we quit
    if regexp_extracted is None:
        return None

    resulted_str = regexp_extracted.string[regexp_extracted.regs[0][0]:regexp_extracted.regs[0][1]]

    #   Check if the resulted string is a numerical value
    if not is_a_numerical_value(resulted_str):
        return None

    #   Convert string to numerical value
    if is_a_int_value(resulted_str):
        return int(resulted_str)

    return float(resulted_str)


#   Used to know the number of sensors based on the first row of a CSV file
def get_sensor_number(csv_row: [str]) -> int:
    #   Check if there is any sensor columns
    if len(csv_row) < 2:
        return 0

    #   Skip temporal column
    index = 1
    array_width = len(csv_row)

    #   Search for the end of the data array or the end of the csv data
    while index < array_width and csv_row[index] != "":
        if csv_row[index] != '':
            index += 1

    return index - 1


#   Used to get the index of the data column from the number of sensors and the first CSV row
def get_next_data_column_index(last_column_index: int, csv_first_row: [str]) -> int:
    #   Skip temporal and sensors column
    index = last_column_index + 1
    array_width = len(csv_first_row)

    #
    if index >= array_width:
        return -1

    #   Search for the end of the data array or the start of the csv situation column
    while index < array_width and csv_first_row[index] == "":
        if csv_first_row[index] == '':
            index += 1

    return index


#   A color gradient that will be #0000FF -> #008000 -> #FF0000 when the provided value is in [0;1]
def get_color_gradient(value: float) -> tuple[int, int, int]:
    #   Value below the lower bound
    if value < 0:
        return 0, 0, 255

    #   Value above the upper bound
    if value > 1:
        return 0, 0, 255

    #   Value is in the middle
    if value == 0.5:
        return 0, 128, 0

    #   For the first half part
    if value < 0.5:
        return 0, int(255 * (value / 0.5)), int(255 * (0.5 - value) / 0.5)

    #   For the last second half part
    return int(255 * ((value - 0.5) / 0.5)), int(255 * abs(1 - value) / 0.5), 0


#   Just a function to parse RGB values to Hex color code
def get_color_hex(value: tuple[int, int, int]) -> str:
    return "#{:0>2X}{:0>2X}{:0>2X}".format(*value)


#   A color gradient that will be #0000FF -> #008000 -> #FF0000 when the provided value is in [0;1]
def get_color_gradient_graph(value: float, lower_alpha: int) -> (int, int, int, int):
    #   Value below the lower bound
    if value == 0:
        return 255, 255, 255, 0

    #   Value above the upper bound
    if value > 1:
        return 0, 0, 255, 255

    #   Value is in the middle
    if value == 0.5:
        return 0, 255, 0, 255

    #   For the first half part
    if value < 0.5:
        return 0, int(255 * (value / 0.5)), int(255 * (0.5 - value) / 0.5), 255

    #   For the last second half part
    return int(255 * ((value - 0.5) / 0.5)), int(255 * abs(1 - value) / 0.5), 0, 255


#   A translator to pass from an array of normalized values to an array of R,G,B colors codes
def get_color_gradient_array(values: [float]) -> list[tuple[int, int, int]]:

    generated_array = list()

    for value in values:
        generated_array.append(get_color_gradient(value))

    return generated_array


#   Just a function to parse RGB values to Hex color code
def get_color_hex_array(values: list[tuple[int, int, int]]) -> [str]:

    generated_array = list()

    for value in values:
        generated_array.append(get_color_hex(value))

    return generated_array


#   To update sliders actual value
def update_slider_value(element: Scale, new_value: int | float) -> None:
    element.set(new_value)


#   To update sliders max value
def update_slider_max(element: Scale, new_value: int | float) -> None:
    element.configure(to=new_value)


#   To lock a tkinter element
def lock(element: Button | Scale | OptionMenu | Entry | Menu | Widget) -> None:
    element['state'] = DISABLED

#   To unlock a tkinter element
def unlock(element: Button | Scale | OptionMenu | Entry | Menu | Widget) -> None:
    element['state'] = NORMAL


#   An ugly function to pass from a svg path to a group of points
def svg_path_to_grp_pts(svg_path: Path) -> [[(int, int)]]:
    #   Abort the process if there is no svg path
    if svg_path.__len__() == 0:
        return []

    generated_array_pts = []
    current_idx = 0
    length = len(svg_path)

    #   Decompose each svg instructions into a groups of points
    for i in range(0, length):
        crt = svg_path[i]
        crt_type = type(crt)
        x, y = int(crt.start.real), int(crt.start.imag)

        if crt_type is Move:
            generated_array_pts.append([(x, y)])

        elif crt_type is Close:
            generated_array_pts[current_idx].append((x, y))
            current_idx += 1

        elif crt_type is Line or crt_type is Arc or crt_type is CubicBezier or crt_type is QuadraticBezier:
            generated_array_pts[current_idx].append((x, y))

    return generated_array_pts


#   An ugly function to pass from multiple svg path to a group of points
def multiple_svg_path_to_grp_pts(svg_path_array: [Path]) -> [[(int, int)]]:
    #   Abort the process if there is no svg path
    if len(svg_path_array) == 0:
        return []

    generated_array_pts = []
    current_idx = 0

    #   Decompose each svg instructions into a groups of points
    for path in svg_path_array:
        length = len(path)

        for i in range(0, length):
            crt = path[i]
            crt_type = type(crt)
            x, y = int(crt.start.real), int(crt.start.imag)

            if crt_type is Move:
                generated_array_pts.append([(x, y)])

            elif crt_type is Close:
                generated_array_pts[current_idx].append((x, y))
                current_idx += 1

            elif crt_type is Line or crt_type is Arc or crt_type is CubicBezier or crt_type is QuadraticBezier:
                generated_array_pts[current_idx].append((x, y))

    return generated_array_pts


#   Translate milliseconds timestamp to a hours, minutes, seconds, milliseconds set
def get_timestamp(value: float) -> (int, int, int, int):

    value_int_ = int(value)

    millis = int(value * 1000) % 1000
    seconds = value_int_ % 60
    minutes = value_int_ // 60 % 60
    hours = value_int_ // 3600 % 24

    return millis, seconds, minutes, hours


#   Translate hours, minutes, seconds, milliseconds set into something formatted and displayable
def get_formatted_timestamp(value: (int, int, int, int)) -> str:
    if value[2] == 0:
        return "{:0>2d}.{:0>3d}".format(value[1], value[0])
    elif value[3] == 0:
        return "{:0>2d}:{:0>2d}.{:0>3d}".format(value[2], value[1], value[0])
    else:
        return "{:0>2d}:{:0>2d}:{:0>2d}.{:0>3d}".format(value[3], value[2], value[1], value[0])


#   Translate milliseconds timestamp into something formatted and displayable
def get_formatted_timestamp_from_value(value: float) -> str:
    return get_formatted_timestamp(get_timestamp(value))


#   Pass from position and sensors characteristics to a center position
def get_sensor_center_position(position: Position, sensor_characteristics: [int, int, int]) -> [Position]:

    #   Calculate each coordinates needed to avoid repetitive calculations
    x_ = position.x + sensor_characteristics[0] // 2
    y_ = position.y + sensor_characteristics[1] // 2

    alpha = math.radians(sensor_characteristics[2])
    cos_alpha = math.cos(alpha)
    sin_alpha = math.sin(alpha)

    #   Initialize position
    return Position(int(x_ * cos_alpha - y_ * sin_alpha),
                    int(x_ * sin_alpha + y_ * cos_alpha))


#   A is in [b1; b2] ?
def a_in_bounds(a: int|float, b1: int|float, b2: int|float) -> bool:
    return b1 <= a <= b2

#   A is in [c1; c2] or B is in [c1; c2] ?
def a_or_b_in_bounds(a: int|float, b: int|float, c1: int|float, c2: int|float) -> bool:
    return a_in_bounds(a, c1, c2) or a_in_bounds(b, c1, c2)
