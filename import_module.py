"""
------------------------------------------------------------------------------------------------------------------------
    Defining application file import module

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""
import csv
from enum import Enum

from dataset import DataSet
from position import Position
from model import Model
from utils import get_file, get_sensor_number, get_situation_data_column_index, is_a_numerical_value


class DataImportModule:
    class ImportTypes(Enum):
        Full_File = 1
        Data_SVG_Files = 2

    __generated_model: Model

    def __init__(self):
        pass

    def get_model_ff_csv(self, file_path: str,
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
            sensors_name: list[str] = csv_data[0][1:nb_of_sensors + 1]

            if nb_of_sensors < 1:
                raise Exception("CSV LOADER: Didn't find any sensors !")

            #   Used to get the first column of sensors situation data in CSV file
            situation_data_index = get_situation_data_column_index(nb_of_sensors, csv_data[0]) + 1

            if situation_data_index == -1:
                raise Exception("CSV LOADER: Didn't find any sensors situation data !")

            #   Initialise sensor arrays
            sensors_data = [[] for _ in range(nb_of_sensors)]
            temporal_set: list[int] = []
            sensors_position: list[Position] = []

            for row in csv_data[1::]:
                #   Get temporal value and sensors values
                temporal_set.append(int(row[0]))
                for i in range(nb_of_sensors):
                    if is_a_numerical_value(row[i + 1]):
                        reformatted_value = row[i + 1].replace(',', '.')
                        sensors_data[i].append(float(reformatted_value))
                    else:
                        raise Exception(
                            "CSV LOADER: Error in values, non numerical value founded for the sensor {:d}".format(i))

            #   Get sensors situation data
            if is_a_numerical_value(csv_data[1][situation_data_index]) and is_a_numerical_value(
                    csv_data[2][situation_data_index]):
                map_height = int(csv_data[1][situation_data_index])
                map_width = int(csv_data[2][situation_data_index])
            else:
                raise Exception(
                    "CSV LOADER: Error in values, non numerical values founded in map size")

            #   Get sensors situation data
            for i in range(nb_of_sensors):
                y_axis = 5 + 3 * i

                if is_a_numerical_value(csv_data[y_axis][situation_data_index]) and is_a_numerical_value(
                        csv_data[y_axis + 1][situation_data_index]):
                    sensors_position.append(Position(int(csv_data[y_axis][situation_data_index]),
                                                     int(csv_data[y_axis + 1][situation_data_index])))
                else:
                    raise ValueError(
                        "CSV LOADER: Error in values, non numerical values founded in position {0}".format(i))

            #   Get sensors
            for i in range(nb_of_sensors):
                y_axis = 5 + 3 * i

                if is_a_numerical_value(csv_data[y_axis][situation_data_index]) and is_a_numerical_value(
                        csv_data[y_axis + 1][situation_data_index]):
                    sensors_position.append(Position(int(csv_data[y_axis][situation_data_index]),
                                                     int(csv_data[y_axis + 1][situation_data_index])))
                else:
                    raise ValueError(
                        "CSV LOADER: Error in values, non numerical values founded in position {0}".format(i))

            #   Initialise a dataset
            self.__generated_model = Model(DataSet(temporal_set, sensors_name, sensors_position, sensors_data,
                                                   map_width, map_height), self)

            return self.__generated_model

        except Exception as e:
            print("An error occurred during the analysis of the given CSV file")
            print("\tException: {0}".format(e))

            on_error(e)
            # raise e
            #   This will indicate an error during the deparsing
            return None
