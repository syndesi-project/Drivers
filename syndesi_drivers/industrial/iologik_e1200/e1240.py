# File : e1240.py
# Author : Sébastien Deriaz
# License : GPL
"""
ioLogik E1240 analog input module

8 analog inputs (0-10 V, 0-20 mA or 4-20 mA), controlled over Modbus TCP
"""

from enum import IntEnum

from .iologik_e1200 import VoltageCurrentInputs

class IoLogikE1240(VoltageCurrentInputs):
    AI_CHANNELS = list(range(8))

    # Modbus map (ioLogik E1200 User's Manual, appendix A)
    class Coil(IntEnum):
        RESET_MIN = 4146
        RESET_MAX = 4154

    class InputRegister(IntEnum):
        # Floats, 2 registers per channel
        AI_VALUE = 9
        AI_MIN = 110
        AI_MAX = 126
        # 1 register per channel
        AI_STATUS = 61

    class HoldingRegister(IntEnum):
        AI_MODE = 25
