# File : adam6217.py
# Author : Sébastien Deriaz
# License : GPL
"""
ADAM-6217 analog input module

8 isolated analog inputs (voltage or current), controlled over Modbus TCP
"""

from enum import IntEnum, IntFlag

from .adam6200 import Adam6200

class Adam6217(Adam6200):
    CHANNELS = list(range(8))
    # Pseudo-channel : average of channels 0 to 7
    AVERAGE = 8

    class Range(IntEnum):
        V_10 = 0x0143       # +/- 10 V
        V_5 = 0x0142        # +/- 5 V
        V_1 = 0x0140        # +/- 1 V
        MV_500 = 0x0104     # +/- 500 mV
        MV_150 = 0x0103     # +/- 150 mV
        MA_20 = 0x0181      # +/- 20 mA
        MA_0_20 = 0x0182    # 0 to 20 mA
        MA_4_20 = 0x0180    # 4 to 20 mA

    class Status(IntFlag):
        UART_TIMEOUT = 1 << 0
        OVER_RANGE = 1 << 1
        UNDER_RANGE = 1 << 2
        OPEN_CIRCUIT = 1 << 3
        ADC_FAILED = 1 << 7
        CALIBRATION_ERROR = 1 << 9

    # Modbus map (ADAM-6200 User Manual, A.1.2)
    class Coil(IntEnum):
        RESET_MAX = 101
        RESET_MIN = 111
        OPEN_CIRCUIT = 121
        HIGH_ALARM = 131
        LOW_ALARM = 141
        CLEAR_GCL_COUNTER = 301

    class Register(IntEnum):
        # IEEE754 floats, 2 registers per channel
        AI_VALUE = 31
        MAX_VALUE = 51
        MIN_VALUE = 71
        # 2 registers per channel
        STATUS = 101
        TYPE_CODE = 201
        CHANNEL_ENABLE = 221
        GCL_FLAGS = 305

    def _check_ai_channel(self, channel : int) -> None:
        self._check_channel(channel, self.CHANNELS + [self.AVERAGE])

    # ┌────────┐
    # │ Values │
    # └────────┘

    def read_analog_in(self, channel : int) -> float:
        """
        Read the value of an analog input

        Parameters
        ----------
        channel : int
            0 to 7, or AVERAGE

        Returns
        -------
        value : float
            Value in engineering units (V or mA)
        """
        self._check_ai_channel(channel)
        return self._read_float(self.Register.AI_VALUE + 2 * channel)

    def read_max(self, channel : int) -> float:
        """
        Read the maximum value of an analog input since the last reset

        Parameters
        ----------
        channel : int
            0 to 7, or AVERAGE

        Returns
        -------
        value : float
        """
        self._check_ai_channel(channel)
        return self._read_float(self.Register.MAX_VALUE + 2 * channel)

    def read_min(self, channel : int) -> float:
        """
        Read the minimum value of an analog input since the last reset

        Parameters
        ----------
        channel : int
            0 to 7, or AVERAGE

        Returns
        -------
        value : float
        """
        self._check_ai_channel(channel)
        return self._read_float(self.Register.MIN_VALUE + 2 * channel)

    def reset_max(self, channel : int) -> None:
        """
        Reset the maximum value to the present value

        Parameters
        ----------
        channel : int
            0 to 7, or AVERAGE
        """
        self._check_ai_channel(channel)
        self._prot.write_single_coil(self.Coil.RESET_MAX + channel, True)

    def reset_min(self, channel : int) -> None:
        """
        Reset the minimum value to the present value

        Parameters
        ----------
        channel : int
            0 to 7, or AVERAGE
        """
        self._check_ai_channel(channel)
        self._prot.write_single_coil(self.Coil.RESET_MIN + channel, True)

    # ┌─────────────────┐
    # │ Status / alarms │
    # └─────────────────┘

    def read_status(self, channel : int) -> Status:
        """
        Read the status of an analog input

        Parameters
        ----------
        channel : int
            0 to 7

        Returns
        -------
        status : Adam6217.Status
            Combination of flags, e.g. Status.OVER_RANGE in status
        """
        self._check_channel(channel, self.CHANNELS)
        return self.Status(self._read_uint32(self.Register.STATUS + 2 * channel))

    def read_open_circuit(self, channel : int) -> bool:
        """
        Return True if an open circuit (burnout) is detected on an analog input

        Parameters
        ----------
        channel : int
            0 to 7

        Returns
        -------
        open_circuit : bool
        """
        self._check_channel(channel, self.CHANNELS)
        return self._prot.read_single_coil(self.Coil.OPEN_CIRCUIT + channel)

    def read_high_alarm(self, channel : int) -> bool:
        """
        Return True if the value is above the high alarm (set in the Advantech utility)

        Parameters
        ----------
        channel : int
            0 to 7, or AVERAGE

        Returns
        -------
        alarm : bool
        """
        self._check_ai_channel(channel)
        return self._prot.read_single_coil(self.Coil.HIGH_ALARM + channel)

    def read_low_alarm(self, channel : int) -> bool:
        """
        Return True if the value is below the low alarm (set in the Advantech utility)

        Parameters
        ----------
        channel : int
            0 to 7, or AVERAGE

        Returns
        -------
        alarm : bool
        """
        self._check_ai_channel(channel)
        return self._prot.read_single_coil(self.Coil.LOW_ALARM + channel)

    # ┌───────────────┐
    # │ Configuration │
    # └───────────────┘

    def set_range(self, channel : int, input_range : Range) -> None:
        """
        Set the input range of an analog input

        Parameters
        ----------
        channel : int
            0 to 7
        input_range : Adam6217.Range
            e.g. Adam6217.Range.V_10
        """
        self._check_channel(channel, self.CHANNELS)
        self._prot.write_single_register(self.Register.TYPE_CODE + channel, self.Range(input_range))

    def get_range(self, channel : int) -> Range:
        """
        Get the input range of an analog input

        Parameters
        ----------
        channel : int
            0 to 7

        Returns
        -------
        input_range : Adam6217.Range
        """
        self._check_channel(channel, self.CHANNELS)
        return self.Range(self._prot.read_single_register(self.Register.TYPE_CODE + channel))

    def enable_channel(self, channel : int, enabled : bool = True) -> None:
        """
        Enable or disable an analog input

        Parameters
        ----------
        channel : int
            0 to 7
        enabled : bool
        """
        self._check_channel(channel, self.CHANNELS)
        value = self._prot.read_single_register(self.Register.CHANNEL_ENABLE)
        if enabled:
            value |= 1 << channel
        else:
            value &= ~(1 << channel)
        self._prot.write_single_register(self.Register.CHANNEL_ENABLE, value)

    def is_channel_enabled(self, channel : int) -> bool:
        """
        Return True if an analog input is enabled

        Parameters
        ----------
        channel : int
            0 to 7

        Returns
        -------
        enabled : bool
        """
        self._check_channel(channel, self.CHANNELS)
        return bool(self._prot.read_single_register(self.Register.CHANNEL_ENABLE) & (1 << channel))
