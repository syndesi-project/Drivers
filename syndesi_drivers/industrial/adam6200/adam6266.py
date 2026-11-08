# File : adam6266.py
# Author : Sébastien Deriaz
# License : GPL
"""
ADAM-6266 IO relay module

4 relay outputs (Form C) and 4 isolated digital inputs, controlled over Modbus TCP

Channel modes (DI, counter, frequency, latch, pulse output, ...) are configured with
the Advantech utility or the web page. This driver only uses the Modbus map
(ADAM-6200 User Manual, A.1.8)
"""

from enum import IntEnum

from syndesi import IP, Driver, Modbus
from syndesi.protocols.modbus import Endian, ModbusMultiRegisterValue

class Adam6266(Driver):
    CHANNELS = list(range(4))
    GCL_COUNTERS = list(range(8))
    GCL_FLAGS = list(range(16))
    # Pulse width resolution (0.1 ms)
    PULSE_WIDTH_UNIT = 1e-4
    # 32-bit values are stored low word first
    WORD_ORDER = Endian.LITTLE

    class Address(IntEnum):
        # Coils (0X)
        DI_VALUES = 1
        DO_VALUES = 17
        COUNTER_START_STOP = 33
        CLEAR_COUNTER = 37
        CLEAR_OVERFLOW = 41
        DI_LATCH_STATUS = 45
        CLEAR_GCL_COUNTER = 301
        # Holding registers (4X, the "4" prefix is dropped : 40001 -> 1)
        # 32-bit values, 2 registers per channel
        COUNTER_FREQUENCY = 1
        PULSE_LOW_WIDTH = 9
        PULSE_HIGH_WIDTH = 17
        ABSOLUTE_PULSE = 25
        INCREMENTAL_PULSE = 33
        GCL_FLAGS = 305

    def __init__(self, adapter : IP) -> None:
        """
        ADAM-6266 relay module

        Parameters
        ----------
        adapter : IP
            Module IP address (Modbus TCP, port 502 by default)
        """
        super().__init__()

        self._prot = Modbus(adapter)

    def _check_channel(self, channel : int):
        if channel not in self.CHANNELS:
            raise ValueError(f"Invalid channel : {channel}, must be in {self.CHANNELS}")

    def _check_states(self, states : list[bool]):
        if len(states) != len(self.CHANNELS):
            raise ValueError(f"Expected {len(self.CHANNELS)} values, got {len(states)}")

    def _read_uint32(self, address : int) -> int:
        return self._prot.read_multi_register_value(address, 2, word_order=self.WORD_ORDER).to_uint()

    def _write_uint32(self, address : int, value : int):
        self._prot.write_multi_register_value(address,
            ModbusMultiRegisterValue.from_uint(int(value), 2, word_order=self.WORD_ORDER))

    # ┌────────────────┐
    # │ Digital inputs │
    # └────────────────┘

    def read_digital_in(self, channel : int) -> bool:
        """
        Read the state of a digital input

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        state : bool
        """
        self._check_channel(channel)
        return self._prot.read_single_coil(self.Address.DI_VALUES + channel)

    def read_digital_ins(self) -> list[bool]:
        """
        Read the state of all digital inputs

        Returns
        -------
        states : list
            One bool per channel
        """
        return self._prot.read_coils(self.Address.DI_VALUES, len(self.CHANNELS))

    def read_latch(self, channel : int) -> bool:
        """
        Read the latch status of a digital input (latch modes only)

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        latched : bool
        """
        self._check_channel(channel)
        return self._prot.read_single_coil(self.Address.DI_LATCH_STATUS + channel)

    def clear_latch(self, channel : int):
        """
        Clear the latch of a digital input

        Parameters
        ----------
        channel : int
            0 to 3
        """
        self._check_channel(channel)
        self._prot.write_single_coil(self.Address.DI_LATCH_STATUS + channel, True)

    # ┌─────────────────────┐
    # │ Counter / frequency │
    # └─────────────────────┘

    def start_counter(self, channel : int):
        """
        Start the counter of a digital input (counter mode only)

        Parameters
        ----------
        channel : int
            0 to 3
        """
        self._check_channel(channel)
        self._prot.write_single_coil(self.Address.COUNTER_START_STOP + channel, True)

    def stop_counter(self, channel : int):
        """
        Stop the counter of a digital input

        Parameters
        ----------
        channel : int
            0 to 3
        """
        self._check_channel(channel)
        self._prot.write_single_coil(self.Address.COUNTER_START_STOP + channel, False)

    def is_counter_running(self, channel : int) -> bool:
        """
        Return True if the counter of a digital input is running

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        running : bool
        """
        self._check_channel(channel)
        return self._prot.read_single_coil(self.Address.COUNTER_START_STOP + channel)

    def clear_counter(self, channel : int):
        """
        Reset the counter of a digital input to 0

        Parameters
        ----------
        channel : int
            0 to 3
        """
        self._check_channel(channel)
        self._prot.write_single_coil(self.Address.CLEAR_COUNTER + channel, True)

    def read_counter(self, channel : int) -> int:
        """
        Read the counter value of a digital input (counter mode only)

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        count : int
            32-bit value
        """
        self._check_channel(channel)
        return self._read_uint32(self.Address.COUNTER_FREQUENCY + 2 * channel)

    def read_frequency(self, channel : int) -> float:
        """
        Read the frequency of a digital input (frequency mode only)

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        frequency : float
            Frequency in Hz (0.1 Hz resolution)
        """
        self._check_channel(channel)
        return self._read_uint32(self.Address.COUNTER_FREQUENCY + 2 * channel) / 10

    def read_counter_overflow(self, channel : int) -> bool:
        """
        Return True if the counter of a digital input has overflowed

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        overflow : bool
        """
        self._check_channel(channel)
        return self._prot.read_single_coil(self.Address.CLEAR_OVERFLOW + channel)

    def clear_counter_overflow(self, channel : int):
        """
        Clear the overflow flag of a counter

        Parameters
        ----------
        channel : int
            0 to 3
        """
        self._check_channel(channel)
        self._prot.write_single_coil(self.Address.CLEAR_OVERFLOW + channel, True)

    # ┌────────┐
    # │ Relays │
    # └────────┘

    def write_relay(self, channel : int, state : bool):
        """
        Set the state of a relay

        Parameters
        ----------
        channel : int
            0 to 3
        state : bool
            True : relay on (NO contact closed), False : relay off
        """
        self._check_channel(channel)
        self._prot.write_single_coil(self.Address.DO_VALUES + channel, bool(state))

    def read_relay(self, channel : int) -> bool:
        """
        Read the state of a relay

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        state : bool
        """
        self._check_channel(channel)
        return self._prot.read_single_coil(self.Address.DO_VALUES + channel)

    def write_relays(self, states : list[bool]):
        """
        Set the state of all relays at once

        Parameters
        ----------
        states : list
            One bool per channel, e.g. [True, False, False, True]
        """
        self._check_states(states)
        self._prot.write_multiple_coils(self.Address.DO_VALUES, [bool(s) for s in states])

    def read_relays(self) -> list[bool]:
        """
        Read the state of all relays

        Returns
        -------
        states : list
            One bool per channel
        """
        return self._prot.read_coils(self.Address.DO_VALUES, len(self.CHANNELS))

    # ┌──────────────┐
    # │ Pulse output │
    # └──────────────┘
    # The relay must be set to "Pulse output" mode. Keep in mind that relays are slow
    # (8 ms set/reset time) and have a limited lifetime

    def set_pulse_width(self, channel : int, low : float, high : float):
        """
        Set the low and high durations of the pulses

        Parameters
        ----------
        channel : int
            0 to 3
        low : float
            Low (off) duration in seconds, 0.1 ms resolution
        high : float
            High (on) duration in seconds, 0.1 ms resolution
        """
        self._check_channel(channel)
        self._write_uint32(self.Address.PULSE_LOW_WIDTH + 2 * channel, round(low / self.PULSE_WIDTH_UNIT))
        self._write_uint32(self.Address.PULSE_HIGH_WIDTH + 2 * channel, round(high / self.PULSE_WIDTH_UNIT))

    def get_pulse_width(self, channel : int) -> tuple[float, float]:
        """
        Get the low and high durations of the pulses

        Parameters
        ----------
        channel : int
            0 to 3

        Returns
        -------
        low : float
            Low (off) duration in seconds
        high : float
            High (on) duration in seconds
        """
        self._check_channel(channel)
        low = self._read_uint32(self.Address.PULSE_LOW_WIDTH + 2 * channel)
        high = self._read_uint32(self.Address.PULSE_HIGH_WIDTH + 2 * channel)
        return low * self.PULSE_WIDTH_UNIT, high * self.PULSE_WIDTH_UNIT

    def generate_pulses(self, channel : int, count : int):
        """
        Generate a number of pulses on a relay

        Parameters
        ----------
        channel : int
            0 to 3
        count : int
            Number of pulses
        """
        self._check_channel(channel)
        self._write_uint32(self.Address.ABSOLUTE_PULSE + 2 * channel, count)

    def add_pulses(self, channel : int, count : int):
        """
        Add pulses to the ones currently being generated

        Parameters
        ----------
        channel : int
            0 to 3
        count : int
            Number of pulses to add
        """
        self._check_channel(channel)
        self._write_uint32(self.Address.INCREMENTAL_PULSE + 2 * channel, count)

    # ┌───────────────────────────────┐
    # │ GCL (Graphic Condition Logic) │
    # └───────────────────────────────┘

    def clear_gcl_counter(self, index : int):
        """
        Reset a GCL internal counter

        Parameters
        ----------
        index : int
            0 to 7
        """
        if index not in self.GCL_COUNTERS:
            raise ValueError(f"Invalid GCL counter : {index}, must be in {self.GCL_COUNTERS}")
        self._prot.write_single_coil(self.Address.CLEAR_GCL_COUNTER + index, True)

    def read_gcl_flags(self) -> list[bool]:
        """
        Read the 16 GCL internal flags

        Returns
        -------
        flags : list
            One bool per flag (0 to 15)
        """
        value = self._prot.read_single_register(self.Address.GCL_FLAGS)
        return [bool(value & (1 << i)) for i in self.GCL_FLAGS]

    def write_gcl_flag(self, index : int, state : bool):
        """
        Set a GCL internal flag

        Parameters
        ----------
        index : int
            0 to 15
        state : bool
        """
        if index not in self.GCL_FLAGS:
            raise ValueError(f"Invalid GCL flag : {index}, must be in {self.GCL_FLAGS}")
        value = self._prot.read_single_register(self.Address.GCL_FLAGS)
        if state:
            value |= 1 << index
        else:
            value &= ~(1 << index)
        self._prot.write_single_register(self.Address.GCL_FLAGS, value)
