"""
------------------------------------------------------------------------------------------------------------------------
    Defining functions and methods used in order to get data from a csv file

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
import re as regexp


def get_file(file_path: str, encoding: str = "ISO-8859-1"):
    return open(file_path, newline='', encoding=encoding)


#   Used to detect difference between a simple string and a string containing a int value
def is_a_int_value(input: str) -> bool:
    #   Check the string with some regex
    return regexp.match("^-?[0-9]+$", input) is not None


#   Used to detect difference between a simple string and a string containing a float or int value
def is_a_numerical_value(input: str) -> bool:
    #   Check the string with some regex
    return regexp.match("^-?[0-9]+((.|,)[0-9]+)?$", input) is not None


#   Used to extract float or int value
#   Will return None if no value was found
def extract_numerical_value(input: str) -> float | int | None:
    #   Extract value from string
    regexp_extracted = regexp.search("-?[0-9]+((.|,)[0-9]+)?", input)

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
def get_color_from_gradient(value: float) -> tuple[int, int, int]:
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
    return int(255 * ((value - 0.5) / 0.5)), int(128 * abs(1 - value) / 0.5), 0


#   Just a function to parse RGB values to Hex color code
def get_color_hex(value: tuple[int, int, int]) -> str:
    return "#{:0>2X}{:0>2X}{:0>2X}".format(*value)
