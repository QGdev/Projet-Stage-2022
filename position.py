"""
------------------------------------------------------------------------------------------------------------------------
    Defining position class

    MIT Licence

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""


class Position:
    x = int
    y = int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def to_string(self) -> str:
        return "x = {0}\ty = {1}".format(self.x, self.y)
