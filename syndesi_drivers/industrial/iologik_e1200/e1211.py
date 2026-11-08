# File : e1211.py
# Author : Sébastien Deriaz
# License : GPL
"""
ioLogik E1211 digital output module

16 digital outputs, controlled over Modbus TCP
"""

from enum import IntEnum

from .iologik_e1200 import DigitalOutputs

class IoLogikE1211(DigitalOutputs):
    DO_CHANNELS = list(range(16))

    # Modbus map (ioLogik E1200 User's Manual, appendix A)
    class Coil(IntEnum):
        DO_STATUS = 1
        PULSE_START_STOP = 17
        WATCHDOG_ALARM = 4145

    class HoldingRegister(IntEnum):
        PULSE_COUNT = 37
        PULSE_ON_WIDTH = 53
        PULSE_OFF_WIDTH = 69
