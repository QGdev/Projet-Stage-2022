#!/usr/bin/env python3
"""
------------------------------------------------------------------------------------------------------------------------
    Program allowing the visualization of the data coming from the sensors in the soles

    The main is just used to launch the program

    MIT Licence

    STAGE 2021 - 2022
        Quentin GOMES DOS REIS
------------------------------------------------------------------------------------------------------------------------
"""

#   Custom modules and classes
from controller import Controller

#   Just here to launch application
if __name__ == '__main__':
    main_controller = Controller()
    main_controller.launch()
