# File : e1210.py
# Author : Sébastien Deriaz
# License : GPL
"""
ioLogik E1210 digital input module

16 digital inputs, controlled over Modbus TCP
"""

from enum import IntEnum

from .iologik_e1200 import DigitalInputs

class IoLogikE1210(DigitalInputs):
    DI_CHANNELS = list(range(16))

    # Modbus map (ioLogik E1200 User's Manual, appendix A)
    class Coil(IntEnum):
        COUNTER_START_STOP = 257
        COUNTER_RESET = 273
        COUNTER_OVERFLOW_CLEAR = 289

    class DiscreteInput(IntEnum):
        DI_STATUS = 1
        COUNTER_OVERFLOW = 1001

    class InputRegister(IntEnum):
        # 32-bit values, 2 registers per channel
        COUNTER_VALUE = 17
