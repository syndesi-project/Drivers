# File : adam6266.py
# Author : Sébastien Deriaz
# License : GPL
"""
ADAM-6266 relay module

4 relay outputs (Form C) and 4 isolated digital inputs, controlled over Modbus TCP
"""

from enum import IntEnum

from .adam6200 import CounterInputs, RelayOutputs

class Adam6266(CounterInputs, RelayOutputs):
    DI_CHANNELS = list(range(4))
    DO_CHANNELS = list(range(4))

    # Modbus map (ADAM-6200 User Manual, A.1.8)
    class Coil(IntEnum):
        DI_VALUE = 1
        DO_VALUE = 17
        COUNTER_START_STOP = 33
        CLEAR_COUNTER = 37
        CLEAR_OVERFLOW = 41
        DI_LATCH = 45
        CLEAR_GCL_COUNTER = 301

    class Register(IntEnum):
        # 32-bit values, 2 registers per channel
        COUNTER_FREQUENCY = 1
        PULSE_LOW_WIDTH = 9
        PULSE_HIGH_WIDTH = 17
        ABSOLUTE_PULSE = 25
        INCREMENTAL_PULSE = 33
        GCL_FLAGS = 305
