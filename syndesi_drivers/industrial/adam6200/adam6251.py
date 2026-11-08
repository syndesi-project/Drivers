# File : adam6251.py
# Author : Sébastien Deriaz
# License : GPL
"""
ADAM-6251 digital input module

16 isolated digital inputs, controlled over Modbus TCP
"""

from enum import IntEnum

from .adam6200 import CounterInputs

class Adam6251(CounterInputs):
    DI_CHANNELS = list(range(16))

    # Modbus map (ADAM-6200 User Manual, A.1.5)
    class Coil(IntEnum):
        DI_VALUE = 1
        COUNTER_START_STOP = 33
        CLEAR_COUNTER = 49
        CLEAR_OVERFLOW = 65
        DI_LATCH = 81
        CLEAR_GCL_COUNTER = 301

    class Register(IntEnum):
        # 32-bit values, 2 registers per channel
        COUNTER_FREQUENCY = 1
        GCL_FLAGS = 305
