# File : adam6224.py
# Author : Sébastien Deriaz
# License : GPL
"""
ADAM-6224 analog output module

4 isolated analog outputs (voltage or current) and 4 digital inputs, controlled over Modbus TCP

The digital inputs can trigger the startup or safety value of the outputs, this is
configured with the Advantech utility
"""

from enum import IntEnum, IntFlag

from .adam6200 import DigitalInputs

class Adam6224(DigitalInputs):
    AO_CHANNELS = list(range(4))
    DI_CHANNELS = list(range(4))
    # 12-bit outputs, 0 -> range minimum, 4095 -> range maximum
    FULL_SCALE = 4095

    class Range(IntEnum):
        MA_0_20 = 0x0182    # 0 to 20 mA
        MA_4_20 = 0x0180    # 4 to 20 mA
        V_0_10 = 0x0148     # 0 to 10 V
        V_0_5 = 0x0147      # 0 to 5 V
        V_10 = 0x0143       # +/- 10 V
        V_5 = 0x0142        # +/- 5 V

    # (minimum, maximum) of each range in V or mA
    RANGE_LIMITS = {
        Range.MA_0_20 : (0, 20),
        Range.MA_4_20 : (4, 20),
        Range.V_0_10 : (0, 10),
        Range.V_0_5 : (0, 5),
        Range.V_10 : (-10, 10),
        Range.V_5 : (-5, 5),
    }

    class OutputStatus(IntFlag):
        # First register
        OUTPUT_FAILED = 1 << 0
        NO_OUTPUT_CURRENT = 1 << 3
        CALIBRATION_ERROR = 1 << 9
        # Second register
        DI_SAFETY_VALUE = 1 << 16
        DI_STARTUP_VALUE = 1 << 17
        FAIL_SAFETY_VALUE = 1 << 18

    class DIEventStatus(IntFlag):
        UART_TIMEOUT = 1 << 0
        SAFETY_VALUE = 1 << 1
        STARTUP_VALUE = 1 << 2

    # Modbus map (ADAM-6200 User Manual, A.1.3)
    class Coil(IntEnum):
        DI_VALUE = 1
        CLEAR_GCL_COUNTER = 301

    class Register(IntEnum):
        AO_VALUE = 1
        # 2 registers per channel
        AO_STATUS = 101
        DI_EVENT_STATUS = 111
        TYPE_CODE = 201
        GCL_FLAGS = 305
        STARTUP_VALUE = 401
        SAFETY_VALUE = 411

    def _to_raw(self, channel : int, value : float) -> int:
        low, high = self.RANGE_LIMITS[self.get_range(channel)]
        if not low <= value <= high:
            raise ValueError(f"Invalid value : {value}, must be in [{low}, {high}]")
        return round((value - low) / (high - low) * self.FULL_SCALE)

    def _from_raw(self, channel : int, raw : int) -> float:
        low, high = self.RANGE_LIMITS[self.get_range(channel)]
        return low + raw / self.FULL_SCALE * (high - low)

    # ┌────────┐
    # │ Values │
    # └────────┘

    def write_analog_out(self, channel : int, value : float) -> None:
        """
        Set the value of an analog output

        Parameters
        ----------
        channel : int
            0 to 3
        value : float
            Value in V or mA, depending on the output range
        """
        self._check_channel(channel, self.AO_CHANNELS)
        self._prot.write_single_register(self.Register.AO_VALUE + channel, self._to_raw(channel, value))

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
            Value in V or mA, depending on the output range
        """
        self._check_channel(channel, self.AO_CHANNELS)
        return self._from_raw(channel, self._prot.read_single_register(self.Register.AO_VALUE + channel))

    def set_startup_value(self, channel : int, value : float) -> None:
        """
        Set the value applied to an analog output at power up

        Parameters
        ----------
        channel : int
            0 to 3
        value : float
            Value in V or mA, depending on the output range
        """
        self._check_channel(channel, self.AO_CHANNELS)
        self._prot.write_single_register(self.Register.STARTUP_VALUE + channel, self._to_raw(channel, value))

    def get_startup_value(self, channel : int) -> float:
        """
        Get the value applied to an analog output at power up

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        value : float
        """
        self._check_channel(channel, self.AO_CHANNELS)
        return self._from_raw(channel, self._prot.read_single_register(self.Register.STARTUP_VALUE + channel))

    def set_safety_value(self, channel : int, value : float) -> None:
        """
        Set the value applied to an analog output on communication loss (watchdog)

        Parameters
        ----------
        channel : int
            0 to 3
        value : float
            Value in V or mA, depending on the output range
        """
        self._check_channel(channel, self.AO_CHANNELS)
        self._prot.write_single_register(self.Register.SAFETY_VALUE + channel, self._to_raw(channel, value))

    def get_safety_value(self, channel : int) -> float:
        """
        Get the value applied to an analog output on communication loss (watchdog)

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        value : float
        """
        self._check_channel(channel, self.AO_CHANNELS)
        return self._from_raw(channel, self._prot.read_single_register(self.Register.SAFETY_VALUE + channel))

    # ┌────────┐
    # │ Status │
    # └────────┘

    def read_output_status(self, channel : int) -> OutputStatus:
        """
        Read the status of an analog output

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        status : Adam6224.OutputStatus
            Combination of flags, e.g. OutputStatus.NO_OUTPUT_CURRENT in status
        """
        self._check_channel(channel, self.AO_CHANNELS)
        first, second = self._prot.read_holding_registers(self.Register.AO_STATUS + 2 * channel, 2)
        return self.OutputStatus(first | second << 16)

    def read_di_event_status(self, channel : int) -> DIEventStatus:
        """
        Read the event status of a digital input

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        status : Adam6224.DIEventStatus
            Combination of flags, e.g. DIEventStatus.SAFETY_VALUE in status
        """
        self._check_channel(channel, self.DI_CHANNELS)
        value = self._prot.read_single_register(self.Register.DI_EVENT_STATUS + channel)
        return self.DIEventStatus(value)

    # ┌───────────────┐
    # │ Configuration │
    # └───────────────┘

    def set_range(self, channel : int, output_range : Range) -> None:
        """
        Set the output range of an analog output

        Parameters
        ----------
        channel : int
            0 to 3
        output_range : Adam6224.Range
            e.g. Adam6224.Range.V_0_10
        """
        self._check_channel(channel, self.AO_CHANNELS)
        self._prot.write_single_register(self.Register.TYPE_CODE + channel, self.Range(output_range))

    def get_range(self, channel : int) -> Range:
        """
        Get the output range of an analog output

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        output_range : Adam6224.Range
        """
        self._check_channel(channel, self.AO_CHANNELS)
        return self.Range(self._prot.read_single_register(self.Register.TYPE_CODE + channel))
