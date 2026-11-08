# File : e1242.py
# Author : Sébastien Deriaz
# License : GPL
"""
ioLogik E1242 analog and digital IO module

4 analog inputs, 4 digital inputs and 4 DIOs, controlled over Modbus TCP

The DIOs are set to DI or DO with jumpers. They are DI 4 to 7 when used as inputs
and DO 0 to 3 when used as outputs
"""

from enum import IntEnum

from .iologik_e1200 import DigitalInputs, DigitalOutputs, VoltageCurrentInputs

class IoLogikE1242(VoltageCurrentInputs, DigitalInputs, DigitalOutputs):
    AI_CHANNELS = list(range(4))
    DI_CHANNELS = list(range(8))
    DO_CHANNELS = list(range(4))

    # Modbus map (ioLogik E1200 User's Manual, appendix A)
    class Coil(IntEnum):
        DO_STATUS = 1
        PULSE_START_STOP = 17
        COUNTER_START_STOP = 257
        COUNTER_RESET = 273
        COUNTER_OVERFLOW_CLEAR = 289
        WATCHDOG_ALARM = 4145
        RESET_MIN = 4146
        RESET_MAX = 4154

    class DiscreteInput(IntEnum):
        DI_STATUS = 1
        COUNTER_OVERFLOW = 1001

    class InputRegister(IntEnum):
        # 32-bit values, 2 registers per channel
        COUNTER_VALUE = 17
        # Floats, 2 registers per channel
        AI_VALUE = 521
        AI_MIN = 537
        AI_MAX = 547
        # 1 register per channel
        AI_STATUS = 577

    class HoldingRegister(IntEnum):
        PULSE_COUNT = 37
        PULSE_ON_WIDTH = 53
        PULSE_OFF_WIDTH = 69
        AI_MODE = 545
