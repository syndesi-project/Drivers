# File : e1262.py
# Author : Sébastien Deriaz
# License : GPL
"""
ioLogik E1262 thermocouple module

8 thermocouple inputs (J, K, T, E, R, S, B, N, or mV), controlled over Modbus TCP
"""

from enum import IntEnum

from .iologik_e1200 import TemperatureInputs

class IoLogikE1262(TemperatureInputs):
    AI_CHANNELS = list(range(8))

    # Modbus map (ioLogik E1200 User's Manual, appendix A)
    class Coil(IntEnum):
        RESET_MIN = 4178
        RESET_MAX = 4186

    class InputRegister(IntEnum):
        # Floats, 2 registers per channel
        AI_VALUE = 2065
        AI_MIN = 2113
        AI_MAX = 2129
