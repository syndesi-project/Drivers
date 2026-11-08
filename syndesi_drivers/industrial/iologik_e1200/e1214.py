# File : e1214.py
# Author : Sébastien Deriaz
# License : GPL
"""
ioLogik E1214 relay module

6 digital inputs and 6 relays, controlled over Modbus TCP
"""

from enum import IntEnum

from .iologik_e1200 import DigitalInputs, RelayOutputs

class IoLogikE1214(DigitalInputs, RelayOutputs):
    DI_CHANNELS = list(range(6))
    DO_CHANNELS = list(range(6))
    # Relay pulse width resolution (1.5 s)
    PULSE_WIDTH_UNIT = 1.5
    # 32-bit pulse counts
    PULSE_COUNT_SIZE = 2

    # Modbus map (ioLogik E1200 User's Manual, appendix A)
    class Coil(IntEnum):
        DO_STATUS = 1
        PULSE_START_STOP = 17
        # The manual says 00048 but the start address is 0048 -> 49
        RELAY_COUNT_RESET = 49
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
        RELAY_TOTAL_COUNT = 65
        RELAY_CURRENT_COUNT = 97

    class HoldingRegister(IntEnum):
        # 2 registers per channel
        PULSE_COUNT = 37
        PULSE_ON_WIDTH = 53
        PULSE_OFF_WIDTH = 69
