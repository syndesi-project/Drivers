# File : e1212.py
# Author : Sébastien Deriaz
# License : GPL
"""
ioLogik E1212 digital IO module

8 digital inputs and 8 DIOs, controlled over Modbus TCP

The DIOs are set to DI or DO with jumpers. They are DI 8 to 15 when used as inputs
and DO 0 to 7 when used as outputs
"""

from enum import IntEnum

from .iologik_e1200 import DigitalInputs, DigitalOutputs

class IoLogikE1212(DigitalInputs, DigitalOutputs):
    DI_CHANNELS = list(range(16))
    DO_CHANNELS = list(range(8))

    # Modbus map (ioLogik E1200 User's Manual, appendix A)
    class Coil(IntEnum):
        DO_STATUS = 1
        PULSE_START_STOP = 17
        COUNTER_START_STOP = 257
        COUNTER_RESET = 273
        COUNTER_OVERFLOW_CLEAR = 289
        WATCHDOG_ALARM = 4145

    class DiscreteInput(IntEnum):
        DI_STATUS = 1
        COUNTER_OVERFLOW = 1001

    class InputRegister(IntEnum):
        # 32-bit values, 2 registers per channel
        COUNTER_VALUE = 17

    class HoldingRegister(IntEnum):
        PULSE_COUNT = 37
        PULSE_ON_WIDTH = 53
        PULSE_OFF_WIDTH = 69
