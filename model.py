"""
------------------------------------------------------------------------------------------------------------------------
    Defining application model

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""

from dataset import DataSet
from position import Position


class Model:
    __dataset: DataSet
    __controller: 'Controller'
    __current_step: int
    __step_number: int
    __is_reverse_enabled: bool
    __is_paused: bool
    __play_speed: float
    __play_speed_factor: float

    def __init__(self, dataset: DataSet, controller: 'Controller'):
        self.__dataset = dataset
        self.__controller = controller
        self.__current_step = 0
        self.__step_number = len(dataset.get_temporal_set())
        self.__is_reverse_enabled = False
        self.__is_paused = True
        self.__play_speed = 1
        self.__play_speed_factor = 1

    #   Get the full dataset (the object)
    def get_dataset(self) -> DataSet:
        return self.__dataset

    #   Get the number of steps
    def get_steps_number(self) -> int:
        return self.__step_number

    #   Get the number of the current steps
    def get_current_step_number(self) -> int:
        return self.__current_step

    #   Get an array of the positions of all sensors
    def get_positions(self) -> [Position]:
        return self.__dataset.get_positions()

    #   Get an array of the data of all sensors at the current step
    def get_current_step_data(self) -> [float]:
        sensor_set = self.__dataset.get_sensor_set()
        return [sensor.get_data_point(self.__current_step) for sensor in sensor_set]

    #   Allow jumping directly to a specified step
    def jump_to_step(self, new_step: int) -> bool:
        if 0 <= new_step < self.__step_number:
            self.__current_step = new_step
            return True
        else:
            return False

    #   To know if there is any other steps after
    def __end_has_been_reached(self) -> bool:
        return (not self.__is_reverse_enabled) and self.__current_step >= self.__step_number - 1

    #   To know if there is any other steps before
    def __start_has_been_reached(self) -> bool:
        return self.__is_reverse_enabled and self.__current_step <= 0

    def bound_reach(self):
        return self.__start_has_been_reached() or self.__end_has_been_reached()

    #   Calculate time delta between next and current step
    def __get_delta_time_next(self) -> int:
        if not self.__end_has_been_reached():
            temporal_set = self.__dataset.get_temporal_set()
            return temporal_set[self.__current_step + 1] - temporal_set[self.__current_step]
        else:
            return 0

    #   Calculate time delta between current and previous step
    def __get_delta_time_prv(self) -> int:
        if not self.__start_has_been_reached():
            temporal_set = self.__dataset.get_temporal_set()
            return temporal_set[self.__current_step] - temporal_set[self.__current_step - 1]
        else:
            return 0

    #   Just pass to the next step in the normal play mode
    def __next_step(self) -> bool:
        if self.__end_has_been_reached():
            return False
        self.__current_step += 1
        return True

    #   Just pass to the next step in the reverse play mode
    def __previous_step(self) -> bool:
        if self.__start_has_been_reached():
            return False

        self.__current_step -= 1
        return True

    #   Just give the time delta depending on the play direction
    def get_delta_time_next(self) -> int:
        #   Pause
        if self.__is_paused:
            return 0
        #   Reverse
        if self.__is_reverse_enabled:
            return self.__get_delta_time_prv()
        #   Normal
        return self.__get_delta_time_next()

    #   Just pass to the next or previous step depending on the play direction
    def next_step(self) -> int:
        #   Pause
        if self.__is_paused:
            return False
        #   Reverse
        if self.__is_reverse_enabled:
            return self.__previous_step()
        #   Normal
        return self.__next_step()

    def play_normal(self) -> None:
        self.__is_reverse_enabled = False

    def play_reverse(self) -> None:
        self.__is_reverse_enabled = True

    def pause(self) -> None:
        self.__is_paused = True

    def play(self) -> None:
        self.__is_paused = False

    def get_play_direction(self) -> int:
        #   Pause
        if self.__is_paused:
            return 0
        #   Reverse
        if self.__is_reverse_enabled:
            return -1
        #   Normal
        return 1

    def is_paused(self) -> bool:
        return self.__is_paused

    def is_reverse_play_enabled(self) -> bool:
        return self.__is_reverse_enabled

    def is_normal_play(self) -> bool:
        return not self.__is_reverse_enabled

    def get_play_speed(self) -> float:
        return self.__play_speed

    def get_play_speed_factor(self) -> float:
        return self.__play_speed_factor

    def set_play_speed(self, new_speed: float):
        if 0.025 <= new_speed <= 2:
            self.__play_speed = new_speed
            self.__play_speed_factor = 1.5 - new_speed * 0.5
