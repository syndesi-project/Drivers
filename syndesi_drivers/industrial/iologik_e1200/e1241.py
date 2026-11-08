# File : e1241.py
# Author : Sébastien Deriaz
# License : GPL
"""
ioLogik E1241 analog output module

4 analog outputs (0-10 V or 4-20 mA), controlled over Modbus TCP

The output mode is selected in the web console and cannot be read over Modbus, it must
be given to the driver so that values can be converted
"""

from enum import Enum, IntEnum

from syndesi import IP

from .iologik_e1200 import Watchdog

class IoLogikE1241(Watchdog):
    AO_CHANNELS = list(range(4))
    # 12-bit outputs, 0 -> range minimum, 4095 -> range maximum
    FULL_SCALE = 4095

    class Mode(Enum):
        VOLTAGE = (0, 10)   # 0 to 10 V
        CURRENT = (4, 20)   # 4 to 20 mA

    # Modbus map (ioLogik E1200 User's Manual, appendix A)
    class Coil(IntEnum):
        WATCHDOG_ALARM = 4145

    class InputRegister(IntEnum):
        # Floats, 2 registers per channel
        AO_VALUE = 1

    class HoldingRegister(IntEnum):
        AO_RAW = 1025

    def __init__(self, adapter : IP, modes : Mode | list[Mode] = Mode.VOLTAGE) -> None:
        """
        ioLogik E1241 analog output module

        Parameters
        ----------
        adapter : IP
            Module IP address (Modbus TCP, port 502 by default)
        modes : Mode or list
            Output mode of each channel, as set in the web console. A single mode
            applies to all channels. Voltage by default
        """
        super().__init__(adapter)

        if isinstance(modes, self.Mode):
            modes = [modes] * len(self.AO_CHANNELS)
        if len(modes) != len(self.AO_CHANNELS):
            raise ValueError(f"Expected {len(self.AO_CHANNELS)} modes, got {len(modes)}")
        self._modes = modes

    def write_analog_out(self, channel : int, value : float) -> None:
        """
        Set the value of an analog output

        Parameters
        ----------
        channel : int
            0 to 3
        value : float
            Value in V or mA, depending on the output mode
        """
        self._check_channel(channel, self.AO_CHANNELS)
        low, high = self._modes[channel].value
        if not low <= value <= high:
            raise ValueError(f"Invalid value : {value}, must be in [{low}, {high}]")
        raw = round((value - low) / (high - low) * self.FULL_SCALE)
        self._prot.write_single_register(self.HoldingRegister.AO_RAW + channel, raw)

    def read_analog_out(self, channel : int) -> float:
        """
        Read the value of an analog output

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        value : float
            Value in V or mA (or in the unit defined by the scaling of the web console)
        """
        self._check_channel(channel, self.AO_CHANNELS)
        return self._read_input_float(self.InputRegister.AO_VALUE + 2 * channel)
