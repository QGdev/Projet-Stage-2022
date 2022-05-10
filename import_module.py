"""
------------------------------------------------------------------------------------------------------------------------
    Defining application file import module

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
import csv
from xml.dom import minidom
from enum import Enum
import svg.path as svg

from dataset import DataSet
from position import Position
from model import Model
from utils import get_file, get_sensor_number, get_next_data_column_index, is_a_numerical_value, is_a_int_value, \
    extract_numerical_value


class DataImportModule:
    class ImportTypes(Enum):
        Full_File = 1
        Data_SVG_Files = 2

    __generated_model: Model

    def __init__(self):
        pass

    #   Full file data (data + positions)
    def get_model_ff(self, file_path: str,
                     on_delimiters_error: 'function',
                     on_error: 'function') -> Model | None:
        try:
            #   file is used to extract data
            #   file_tmp is used to get the first line and the file is closed immediately after
            file = get_file(file_path)
            file_tmp = get_file(file_path)

            if not (file.readable() or file_tmp.readable()):
                raise Exception("Selected file isn't readable !")

            first_line = file_tmp.readline()
            file_tmp.close()

            #   Get CSV parameters of the selected CSV file
            csv_parameters = csv.Sniffer().sniff(first_line)

            #   The CSV sniffer couldn't detect CSV structure
            #   Ask user to provide delimiters manually
            if csv_parameters is None:
                answered_delimiter = on_delimiters_error()
                csv_parameters = csv.Sniffer().sniff(first_line, answered_delimiter)

            #   Parse the CSV into an iterator
            csv_reader = csv.reader(file, delimiter=csv_parameters.delimiter,
                                    quotechar=csv_parameters.quotechar, quoting=csv_parameters.quoting)
            #   Unpack interator content
            csv_data = [*csv_reader]

            #   Get sensors names and the number of sensors
            nb_of_sensors = get_sensor_number(csv_data[0])
            sensors_name: [str] = csv_data[0][1:nb_of_sensors + 1]

            if nb_of_sensors < 1:
                raise Exception("CSV LOADER: Didn't find any sensors !")

            #   Used to get the first column of sensors situation data in CSV file
            situation_data_index = get_next_data_column_index(nb_of_sensors, csv_data[0]) + 1

            if situation_data_index == -1:
                raise Exception("CSV LOADER: Didn't find any sensors situation data !")

            #   Initialise sensor arrays
            sensors_data = [[] for _ in range(nb_of_sensors)]
            temporal_set: [float] = []
            sensors_position: [Position] = []

            for row in csv_data[1::]:
                #   Get temporal value
                if is_a_numerical_value(row[0]):
                    temporal_set.append(float(row[0].replace(',', '.')) * 0.001)
                else:
                    raise Exception(
                        "CSV LOADER: Error in time values, non numerical value found {:s}".format(row[0]))

                #   Get sensors data
                for i in range(nb_of_sensors):
                    if is_a_numerical_value(row[i + 1]):
                        reformatted_value = row[i + 1].replace(',', '.')
                        sensors_data[i].append(float(reformatted_value))
                    else:
                        raise Exception(
                            "CSV LOADER: Error in values, non numerical value found for the sensor {:d}".format(i))

            #   Get map size data
            if is_a_numerical_value(csv_data[1][situation_data_index]) and is_a_numerical_value(csv_data[2][situation_data_index]):
                map_height = int(csv_data[1][situation_data_index])
                map_width = int(csv_data[2][situation_data_index])
            else:
                raise Exception(
                    "CSV LOADER: Error in values, non numerical values found in map size")

            #   Get sensors situation data
            for i in range(nb_of_sensors):
                y_axis = 5 + 3 * i

                if is_a_numerical_value(csv_data[y_axis][situation_data_index]) and is_a_numerical_value(
                        csv_data[y_axis + 1][situation_data_index]):
                    sensors_position.append(Position(int(csv_data[y_axis][situation_data_index]),
                                                     int(csv_data[y_axis + 1][situation_data_index])))
                else:
                    raise ValueError(
                        "CSV LOADER: Error in values, non numerical values found in position {0}".format(i))

            sensors_size_data_index = get_next_data_column_index(situation_data_index, csv_data[5]) + 1

            #   Get sensors size data
            if is_a_int_value(csv_data[5][sensors_size_data_index]) and is_a_int_value(csv_data[6][sensors_size_data_index]):
                sensors_height = int(csv_data[5][sensors_size_data_index])
                sensors_width = int(csv_data[6][sensors_size_data_index])
            else:
                raise Exception(
                    "CSV LOADER: Error in values, non integer values found in sensors size")

            #   Initialise a dataset
            self.__generated_model = Model(DataSet(temporal_set, sensors_name, sensors_position,
                                                   [[sensors_width, sensors_height, 0] for _ in range(nb_of_sensors)],
                                                   sensors_data, map_width, map_height), self)

            return self.__generated_model

        except Exception as e:
            print("An error occurred during the analysis of the given CSV file")
            print("\tException: {0}".format(e))

            on_error(e)
            raise e

    #
    #
    #   Data + SVG files import
    def get_model_dsf(self,
                      file_path: str,
                      svg_file_path: str,
                      on_delimiters_error: 'function',
                      on_position_error: 'function',
                      on_error: 'function'):
        try:
            #   Try to open each provided files to fail immediately if a file cannot be opened or if is unreadable

            #   file is used to extract data
            #   file_tmp is used to get the first line and the file is closed immediately after use
            #   file_svg = get_file(svg_file_path)
            file = get_file(file_path)
            file_tmp = get_file(file_path)
            file_svg = get_file(svg_file_path)

            if not (file.readable() or file_tmp.readable()):
                raise Exception("Selected CSV file isn't readable !")

            if not (file_svg.readable()):
                raise Exception("Selected SVG file isn't readable !")

            first_line = file_tmp.readline()
            file_tmp.close()

            #   Get CSV parameters of the selected CSV file
            csv_parameters = csv.Sniffer().sniff(first_line)

            #   The CSV sniffer couldn't detect CSV structure
            #   Ask user to provide delimiters manually
            if csv_parameters is None:
                answered_delimiter = on_delimiters_error()
                csv_parameters = csv.Sniffer().sniff(first_line, answered_delimiter)

            #   Parse the CSV into an iterator
            csv_reader = csv.reader(file, delimiter=csv_parameters.delimiter,
                                    quotechar=csv_parameters.quotechar, quoting=csv_parameters.quoting)
            #   Unpack interator content
            csv_data = [*csv_reader]

            #   Get sensors names and the number of sensors
            nb_of_sensors = len(csv_data[0]) - 1
            sensors_name: [str] = csv_data[0][1:nb_of_sensors + 1]

            if nb_of_sensors < 1:
                raise Exception("CSV LOADER: Didn't find any sensors !")

            #   Initialise sensor arrays
            sensors_data = [[] for _ in range(nb_of_sensors)]
            temporal_set: [float] = []

            for row in csv_data[1::]:
                if row[0] != "--":
                    #   Get temporal value
                    if is_a_numerical_value(row[0]):
                        temporal_set.append(float(row[0].replace(',', '.')))
                    else:
                        raise Exception(
                            "CSV LOADER: Error in time values, non numerical value found {:s}".format(row[0]))

                    #   Get sensors values
                    for i in range(nb_of_sensors):
                        if is_a_int_value(row[i + 1]):
                            sensors_data[i].append(float(row[i + 1]))

                        elif is_a_numerical_value(row[i + 1]):
                            sensors_data[i].append(float(row[i + 1].replace(',', '.')))
                        else:
                            raise Exception(
                                "CSV LOADER: Error in values, non numerical value found for the sensor {:d}".format(i))

        except Exception as e:
            print("An error occurred during the analysis of the given CSV file")
            print("\tException: {0}".format(e))

            on_error(e)
            #   raise e
            return None

        try:
            #   Now, we will analyse SVG file
            svg_xml = minidom.parse(file_svg).getElementsByTagName("svg")[0]

            #   Extract map width and height from svg
            map_width = extract_numerical_value(svg_xml.attributes["width"].value)
            map_height = extract_numerical_value(svg_xml.attributes["height"].value)

            if map_width is None or map_height is None:
                raise Exception("SVG LOADER: Error in map width or height value")

            sensors_characteristics = [[] for _ in range(nb_of_sensors)]
            sensors_position: [Position | None] = [None for _ in range(nb_of_sensors)]

            #   Extract sensors positions and dimensions from svg
            rect_xml = svg_xml.getElementsByTagName("rect")

            for rect in rect_xml:
                index = sensors_name.index(rect.attributes["id"].value)

                #   The analysed sensor from the SVG didn't match with CSV data
                if index == -1:
                    Exception("SVG LOADER: Error cannot match the sensor {:s} with CSV data".format(rect.attributes["id"].value))

                #   Check for any duplication
                if len(sensors_characteristics[index]) > 0 or sensors_position[index] is None:
                    Exception("SVG LOADER: Error in duplication found for the sensor {:s} in SVG".format(rect.attributes["id"].value))

                #   Extract sensors_characteristics
                if 'transform' in rect.attributes:
                    sensors_characteristics[index] = [int(extract_numerical_value(rect.attributes["width"].value)),
                                                      int(extract_numerical_value(rect.attributes["height"].value)),
                                                      int(extract_numerical_value(rect.attributes["transform"].value))]
                else:
                    sensors_characteristics[index] = [int(extract_numerical_value(rect.attributes["width"].value)),
                                                      int(extract_numerical_value(rect.attributes["height"].value)),
                                                      0]

                if sensors_characteristics[index][0] <= 0 or sensors_characteristics[index][1] <= 0:
                    Exception("SVG LOADER: Error in height and width found for the sensor {:s} in SVG".format(rect.attributes["id"].value))

                sensors_position[index] = Position(int(extract_numerical_value(rect.attributes["x"].value)),
                                                   int(extract_numerical_value(rect.attributes["y"].value)))

            #   Initialise a dataset
            self.__generated_model = Model(DataSet(temporal_set, sensors_name, sensors_position,
                                                   sensors_characteristics, sensors_data,
                                                   map_width, map_height), self)

            svg_bg_xml = svg_xml.getElementsByTagName("path")

            svg_bg_path = list()

            for svg_bg in svg_bg_xml:
                if svg_bg.attributes['id'].value == "BG_PATH":
                    svg_bg_path.append(svg.parse_path(svg_bg.attributes['d'].value))

            return self.__generated_model, svg_bg_path


        except Exception as e:
            print("An error occurred during the analysis of the given SVG file")
            print("\tException: {0}".format(e))

            on_position_error(e)
            raise e
            #   This will indicate an error during the deparsing
            return None
