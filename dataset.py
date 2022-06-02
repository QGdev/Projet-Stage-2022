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
from utils import get_sensor_center_position


class DataSet:
    __sensor_set: [ForceSensor]
    __sensor_set_max: float
    __sensor_set_min: float
    __sensor_set_max_norm: float
    __sensor_set_min_norm: float
    __is_normalized: bool

    __temporal_set: [float]

    __center_of_mass_positions_calculated: bool
    __center_of_mass_positions: [Position]

    __map_width: int
    __map_height: int

    def __init__(self, temporal_set: [int], sensors_name: [str], sensors_positions: [Position],
                 sensors_characteristics: [[int, int, int]], sensors_data: [[float]],
                 map_width: int, map_height: int):

        #   Data consistency check:
        #   1 - sensors_name, sensors_data and temporal_set must have at least one element
        #   2 - Number of elements in sensors_name must be the same as the number of arrays in sensors_data and
        #       the same number of position in sensors_position and in sensors_characteristics
        #   3 - The temporal_set cannot have negative values
        #   4 - The temporal_set must have chronological values in increasingly way
        #   5 - Each sensor must have the same number of values as the others. (if there is more than one sensor)
        #   6 - Each provided positions must be in included in map bounds

        #   Verification of the point 1
        if len(temporal_set) < 1 or len(sensors_name) < 1 or len(sensors_data) < 1:
            raise Exception(
                "Data consistency error: No enough data in the temporal set, sensors name set or sensors number !")

        #   Verification of the point 2
        if len(sensors_name) != len(sensors_data) and len(sensors_data) != len(sensors_positions):
            raise Exception(
                "Data consistency error: Incompatibility between the number of sensors names, the number of sensors, the number of positions !")

        #   Verification of the point 3
        if min(temporal_set) < 0:
            raise Exception(
                "Data consistency error: Temporal set inconsistency, cannot have negative values in temporal set !")

        #   Verification of the point 4
        tmp_value = temporal_set[0]
        for i in range(1, len(temporal_set)):
            if tmp_value > temporal_set[i]:
                raise Exception("Data consistency error: Temporal set inconsistency, not chronological !")

        #   Verification of the point 5 only for the first sensor
        if len(sensors_data[0]) < 1:
            raise Exception(
                "Data consistency error: No enough data in sensor #1 data set !")

        #   Verification of the point 5 only for each sensor
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
        for i in range(0, len(sensors_positions)):
            if (0 > sensors_positions[i].x > map_width) or (0 > sensors_positions[i].y > map_height):
                raise Exception(
                    "Data consistency error: The position of the sensor #{:d} is out of map bounds !".format(i + 1))

        #   End of the data consistency check:

        #   Now, let's create all sensors
        self.__sensor_set = []

        for i in range(0, len(sensors_data)):
            if sensors_characteristics[i][0] < 0 or sensors_characteristics[i][1] < 0:
                raise Exception(
                    "Data consistency error: Characteristics of the sensor #{:d} are invalid !".format(i + 1))

            self.__sensor_set.append(ForceSensor(sensors_name[i],
                                                 sensors_positions[i],
                                                 get_sensor_center_position(sensors_positions[i],
                                                                            sensors_characteristics[i]),
                                                 sensors_characteristics[i][0],
                                                 sensors_characteristics[i][1],
                                                 sensors_characteristics[i][2],
                                                 sensors_data[i]))

        self.__sensor_set_min = min([i.data_min for i in self.__sensor_set])
        self.__sensor_set_max = max([i.data_max for i in self.__sensor_set])

        self.__sensor_set_min_norm = 0
        self.__sensor_set_max_norm = 0

        self.__temporal_set = temporal_set
        self.__is_normalized = False
        self.__map_width = map_width
        self.__map_height = map_height

        #   Debug statement just to show values before normalization
        # for x in self.__sensor_set:
        #    print("{:s}:\t{:.4f}\t/\t{:.4f}".format(x.get_name(), x.get_max(), x.get_min()))

        if not self.normalize_sensors():
            raise Exception("Cannot normalize sensors data")

        if not self.center_of_mass_position_calculation():
            raise Exception("Cannot calculate position of the center of mass")

    def normalize_sensors(self) -> bool:
        operation_success = True

        normalized_values = (abs(self.__sensor_set_min), abs(self.__sensor_set_max) + abs(self.__sensor_set_min))

        #   Browse our entire sensor set
        for sensor in self.__sensor_set:
            operation_success = sensor.normalize_data(*normalized_values)

            #   Exit the loop if a sensor normalisation fails
            if not operation_success:
                break

        if operation_success:
            self.__sensor_set_min_norm = min([sensor.data_min_norm for sensor in self.__sensor_set])
            self.__sensor_set_max_norm = max([sensor.data_max_norm for sensor in self.__sensor_set])

        #   Update normalisation status of the data set
        self.__is_normalized = operation_success
        return operation_success

    def center_of_mass_position_calculation(self) -> bool:

        generated_center_of_mass_positions: [Position] = list()

        #   Browse each measurement and pick each data and position of the sensor
        for i in range(len(self.__temporal_set)):
            sensors_data_sum: float = 0
            x: float = 0
            y: float = 0

            for sensor in self.__sensor_set:

                sensor_data = sensor.get_data_point_normalized(i)
                sensors_data_sum += sensor_data

                x += sensor_data * sensor.get_center_position().x
                y += sensor_data * sensor.get_center_position().y

            if sensors_data_sum == 0:
                self.__center_of_mass_positions_calculated = False
                return False

            generated_center_of_mass_positions.append(Position(int(x / sensors_data_sum),
                                                               int(y / sensors_data_sum)))

        #   Update status of positions calculation of the center of mass
        self.__center_of_mass_positions_calculated = True
        self.__center_of_mass_positions = generated_center_of_mass_positions
        return True

    def get_sensor_set(self) -> [ForceSensor]:
        return self.__sensor_set

    def get_number_of_sensors(self) -> int:
        return len(self.__sensor_set)

    def get_sensor_set_max_norm(self) -> float:
        return self.__sensor_set_max_norm

    def get_sensor_set_min_norm(self) -> float:
        return self.__sensor_set_min_norm

    def get_sensor_set_max(self) -> float:
        return self.__sensor_set_max

    def get_sensor_set_min(self) -> float:
        return self.__sensor_set_min

    def get_temporal_set(self) -> [float]:
        return self.__temporal_set

    def is_normalized(self) -> bool:
        return self.__is_normalized

    def is_ctr_of_mass_pos_calculated(self) -> bool:
        return self.__center_of_mass_positions_calculated

    def get_map_width(self) -> int:
        return self.__map_width

    def get_map_height(self) -> int:
        return self.__map_height

    def get_positions(self) -> [Position]:
        return [sensor.get_position() for sensor in self.__sensor_set]

    def get_centers(self) -> [Position]:
        return [sensor.get_center_position() for sensor in self.__sensor_set]

    def get_sensor_names(self) -> [str]:
        return [sensor.get_name() for sensor in self.__sensor_set]

    def get_sensors_max(self) -> [float]:
        return [sensor.get_max() for sensor in self.__sensor_set]

    def get_sensors_min(self) -> [float]:
        return [sensor.get_min() for sensor in self.__sensor_set]

    def get_sensors_max_normalized(self) -> [float]:
        return [sensor.get_max_normalized() for sensor in self.__sensor_set]

    def get_sensors_min_normalized(self) -> [float]:
        return [sensor.get_min_normalized() for sensor in self.__sensor_set]

    def get_sensors_values(self) -> [float]:
        return [sensor.get_data() for sensor in self.__sensor_set]

    def get_sensors_normalized_values(self) -> [float]:
        return [sensor.get_data_normalized() for sensor in self.__sensor_set]

    def get_sensors_values_at(self, index: int) -> [float]:
        return [sensor.get_data_point(index) for sensor in self.__sensor_set]

    def get_sensors_normalized_values_at(self, index: int) -> [float]:
        return [sensor.get_data_point_normalized(index) for sensor in self.__sensor_set]

    #   Will return an array filled with all sensors characteristics [width, height, angle]
    def get_sensors_characteristics(self) -> [[int, int, int]]:
        return [sensor.get_characteristics() for sensor in self.__sensor_set]

    def get_c_o_m_positions(self) -> [Position]:
        return self.__center_of_mass_positions
