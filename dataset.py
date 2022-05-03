"""
------------------------------------------------------------------------------------------------------------------------
    Defining a dataset which will contain all sensors and global variables related to our dataset

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""

#   Custom modules and classes
from force_sensor import ForceSensor
from position import Position


class DataSet:
    __sensor_set: [ForceSensor]
    __sensor_set_max: float
    __sensor_set_min: float
    __temporal_set: [int]
    __is_normalized: bool
    __normalize_values: (float, float)
    __map_width: int
    __map_height: int
    __figure_width: int
    __figure_height: int

    def __init__(self, temporal_set: [int], sensors_name: [str], sensors_position: [Position], sensors_data: [[float]],
                 map_width: int, map_height: int):

        #   Data consistency check:
        #   1 - sensors_name, sensors_data and temporal_set must have at least one element
        #   2 - Number of elements in sensors_name must be the same as the number of arrays in sensors_data and
        #       the same number of position in sensors_position
        #   3 - The temporal_set cannot have negative values
        #   4 - Each sensor must have the same number of values as the others. (if there is more than one sensor)
        #   5 - Each provided positions must be in included in map bounds

        #   Verification of the point 1
        if len(temporal_set) < 1 or len(sensors_name) < 1 or len(sensors_data) < 1:
            raise Exception(
                "Data consistency error: No enough data in the temporal set, sensors name set or sensors number !")

        #   Verification of the point 2
        if len(sensors_name) != len(sensors_data) and len(sensors_data) != len(sensors_position):
            raise Exception(
                "Data consistency error: Incompatibility between the number of sensors names, the number of sensors, the number of positions !")

        #   Verification of the point 3
        if min(temporal_set) < 0:
            raise Exception(
                "Data consistency error: Temporal set inconsistency, cannot have negative values in temporal set !")

        #   Verification of the point 4 only for the first sensor
        if len(sensors_data[0]) < 1:
            raise Exception(
                "Data consistency error: No enough data in sensor #1 data set !")

        #   Verification of the point 4 only for each sensor
        if len(sensors_data) > 1:
            last_length = len(sensors_data[0])

            for i in range(1, len(sensors_data)):
                last_length_tmp = len(sensors_data[i])

                if last_length_tmp < 1:
                    raise Exception("Data consistency error: No enough data in sensor #{:d} data set !".format(i + 1))

                if last_length_tmp != last_length:
                    raise Exception("Data consistency error: No enough data in sensor #{:d} data set !".format(i + 1))

                last_length = last_length_tmp

        #   Verification of the point 6 for each sensor
        for i in range(0, len(sensors_position)):
            if (0 > sensors_position[i].x > map_width) or (0 > sensors_position[i].y > map_height):
                raise Exception(
                    "Data consistency error: The position of the sensor #{:d} is out of map bounds !".format(i + 1))

        #   End of the data consistency check:

        self.__sensor_set = []

        for i in range(0, len(sensors_data)):
            self.__sensor_set.append(ForceSensor(sensors_name[i],
                                                 sensors_position[i],
                                                 sensors_data[i]))

        self.__sensor_set_min = min([i.data_min for i in self.__sensor_set])
        self.__sensor_set_max = max([i.data_max for i in self.__sensor_set])

        self.__normalize_values = (abs(self.__sensor_set_min), abs(self.__sensor_set_max) + abs(self.__sensor_set_min))

        self.__temporal_set = temporal_set
        self.__is_normalized = False
        self.__map_width = map_width
        self.__map_height = map_height

        #   Debug statement just to show values before normalization
        # for x in self.__sensor_set:
        #    print("{:s}:\t{:.4f}\t/\t{:.4f}".format(x.get_name(), x.get_max(), x.get_min()))

        self.normalize_sensors()

    def normalize_sensors(self) -> bool:
        operation_success = True

        #   Browse our entire sensor set
        for sensor in self.__sensor_set:
            operation_success = sensor.normalize_data(self.__normalize_values[0], self.__normalize_values[1])

            #   Exit the loop if a sensor normalisation fails
            if not operation_success:
                break

        if operation_success:
            self.__sensor_set_min = min([i.data_min for i in self.__sensor_set])
            self.__sensor_set_max = max([i.data_max for i in self.__sensor_set])

        #   Update normalisation status of the data set
        self.__is_normalized = operation_success
        return operation_success

    def get_sensor_set(self) -> [ForceSensor]:
        return self.__sensor_set

    def get_sensor_set_max_norm(self) -> float:
        return self.__sensor_set_max

    def get_sensor_set_min_norm(self) -> float:
        return self.__sensor_set_min

    def get_sensor_set_max(self) -> float:
        return self.__sensor_set_max * self.__normalize_values[1] - self.__normalize_values[0]

    def get_sensor_set_min(self) -> float:
        return self.__sensor_set_min * self.__normalize_values[1] - self.__normalize_values[0]

    def get_temporal_set(self) -> [float]:
        return self.__temporal_set

    def is_normalized(self) -> int:
        return self.__is_normalized

    def get_map_width(self) -> int:
        return self.__map_width

    def get_map_height(self) -> int:
        return self.__map_height

    def get_positions(self) -> [Position]:
        return [sensor.get_position() for sensor in self.__sensor_set]

    def get_sensor_names(self) -> [str]:
        return [sensor.get_name() for sensor in self.__sensor_set]

    def get_sensors_max(self) -> [float]:
        return [sensor.get_max() for sensor in self.__sensor_set]

    def get_sensors_min(self) -> [float]:
        return [sensor.get_min() for sensor in self.__sensor_set]

    def denormalize(self, value: float) -> float:
        return value * self.__normalize_values[1] - self.__normalize_values[0]

    def get_sensors_max_denormalized(self) -> [float]:
        return [self.denormalize(sensor.get_max()) for sensor in self.__sensor_set]

    def get_sensors_min_denormalized(self) -> [float]:
        return [self.denormalize(sensor.get_min()) for sensor in self.__sensor_set]
