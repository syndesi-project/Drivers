# File : adam6250.py
# Author : Sébastien Deriaz
# License : GPL
"""
ADAM-6250 digital IO module

8 isolated digital inputs and 7 isolated digital outputs, controlled over Modbus TCP
"""

from enum import IntEnum

from .adam6200 import CounterInputs, DigitalOutputs

class Adam6250(CounterInputs, DigitalOutputs):
    DI_CHANNELS = list(range(8))
    DO_CHANNELS = list(range(7))

    # Modbus map (ADAM-6200 User Manual, A.1.4)
    class Coil(IntEnum):
        DI_VALUE = 1
        DO_VALUE = 17
        COUNTER_START_STOP = 33
        CLEAR_COUNTER = 41
        CLEAR_OVERFLOW = 49
        DI_LATCH = 57
        CLEAR_GCL_COUNTER = 301

    class Register(IntEnum):
        # 32-bit values, 2 registers per channel
        COUNTER_FREQUENCY = 1
        PULSE_LOW_WIDTH = 17
        PULSE_HIGH_WIDTH = 31
        ABSOLUTE_PULSE = 45
        INCREMENTAL_PULSE = 59
        GCL_FLAGS = 305
