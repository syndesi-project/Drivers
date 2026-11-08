# File : adam6260.py
# Author : Sébastien Deriaz
# License : GPL
"""
ADAM-6260 relay module

6 relay outputs (5 Form C, 1 Form A), controlled over Modbus TCP
"""

from enum import IntEnum

from .adam6200 import RelayOutputs

class Adam6260(RelayOutputs):
    DO_CHANNELS = list(range(6))

    # Modbus map (ADAM-6200 User Manual, A.1.7)
    class Coil(IntEnum):
        DO_VALUE = 17
        CLEAR_GCL_COUNTER = 301

    class Register(IntEnum):
        # 32-bit values, 2 registers per channel
        PULSE_LOW_WIDTH = 1
        PULSE_HIGH_WIDTH = 13
        ABSOLUTE_PULSE = 25
        INCREMENTAL_PULSE = 37
        GCL_FLAGS = 305
