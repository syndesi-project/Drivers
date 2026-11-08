# File : e1260.py
# Author : Sébastien Deriaz
# License : GPL
"""
ioLogik E1260 RTD module

6 RTD inputs (PT50 to PT1000, or resistance), controlled over Modbus TCP
"""

from enum import IntEnum

from .iologik_e1200 import TemperatureInputs

class IoLogikE1260(TemperatureInputs):
    AI_CHANNELS = list(range(6))

    # Modbus map (ioLogik E1200 User's Manual, appendix A)
    class Coil(IntEnum):
        RESET_MIN = 4162
        RESET_MAX = 4170

    class InputRegister(IntEnum):
        # Floats, 2 registers per channel
        AI_VALUE = 1549
        AI_MIN = 1585
        AI_MAX = 1597
