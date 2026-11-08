# File : adam6256.py
# Author : Sébastien Deriaz
# License : GPL
"""
ADAM-6256 digital output module

16 isolated digital outputs, controlled over Modbus TCP
"""

from enum import IntEnum

from .adam6200 import DigitalOutputs

class Adam6256(DigitalOutputs):
    DO_CHANNELS = list(range(16))

    # Modbus map (ADAM-6200 User Manual, A.1.6)
    class Coil(IntEnum):
        DO_VALUE = 17
        CLEAR_GCL_COUNTER = 301

    class Register(IntEnum):
        # 32-bit values, 2 registers per channel
        PULSE_LOW_WIDTH = 1
        PULSE_HIGH_WIDTH = 33
        ABSOLUTE_PULSE = 65
        INCREMENTAL_PULSE = 97
        GCL_FLAGS = 305
