"""
------------------------------------------------------------------------------------------------------------------------
    Defining force sensor class

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""

from position import Position


class ForceSensor:
    name: str
    data: [float]
    data_max: float
    data_min: float
    position: Position

    def __init__(self, name: str, position: Position, data: [float]):
        self.name = name
        self.data = data
        self.data_min = min(data)
        self.data_max = max(data)
        self.position = position

    def get_min(self) -> float:
        return self.data_min

    def get_max(self) -> float:
        return self.data_max

    def get_data(self) -> [float]:
        return self.data

    def get_data_point(self, index: int) -> float:
        return self.data[index]

    def get_position(self) -> Position:
        return self.position

    def get_name(self) -> str:
        return self.name

    def normalize_data(self, add_value: float, division_value: float) -> bool:
        #   Normalize each values
        for i in range(0, len(self.data)):
            self.data[i] += add_value
            self.data[i] /= division_value

        #   Update max and min for the sensor with new max and new min
        self.data_max = max(self.data)
        self.data_min = min(self.data)

        #   Return the operation end status
        #   If the operation have succeeded new min and max must be contained in [0; 1]
        return self.data_min >= 0 and self.data_max <= 1

    def to_string(self) -> str:
        return "{0} : {1}\tmin:{2}\tmax:{3}\tdata:{4}".format(self.name, self.position.to_string(),
                                                              self.data_min, self.data_max, self.data)
