# File : adam6200.py
# Author : Sébastien Deriaz
# License : GPL
"""
Common base for the ADAM-6200 series (Modbus TCP IO modules)

Each module declares its own Modbus map (ADAM-6200 User Manual, appendix A) in two enums :
- Coil : coils (0X, function codes 01, 05, 0F)
- Register : holding registers (4X, function codes 03, 06, 10)

Coils and holding registers are two separate tables, the same number can be used in both.
The "4" prefix of the manual is dropped : 40001 -> 1

Channel modes (counter, frequency, latch, pulse output, ...) are configured with the
Advantech utility or the web page
"""

from typing import Any

from syndesi import IP, Driver, Modbus
from syndesi.protocols.modbus import Endian, ModbusMultiRegisterValue

class Adam6200(Driver):
    GCL_COUNTERS = list(range(8))
    GCL_FLAGS = list(range(16))
    # 32-bit values are stored low word first
    WORD_ORDER = Endian.LITTLE
    # Modbus map, defined by each module
    Coil : Any
    Register : Any

    def __init__(self, adapter : IP) -> None:
        """
        ADAM-6200 module

        Parameters
        ----------
        adapter : IP
            Module IP address (Modbus TCP, port 502 by default)
        """
        super().__init__()

        assert isinstance(adapter, IP), "Invalid adapter"
        self._prot = Modbus(adapter)

    def open(self) -> None:
        """
        Open the connection (done automatically on the first request)
        """
        self._prot.open()

    def close(self) -> None:
        """
        Close the connection
        """
        self._prot.close()

    def test(self) -> bool:
        """
        Test presence of the module

        Returns
        -------
        success : bool
        """
        try:
            self._prot.read_single_register(self.Register.GCL_FLAGS)
            return True
        except Exception:
            return False

    def _check_channel(self, channel : int, channels : list[int], name : str = "channel") -> None:
        if channel not in channels:
            raise ValueError(f"Invalid {name} : {channel}, must be in {channels}")

    def _check_states(self, states : list[bool], channels : list[int]) -> None:
        if len(states) != len(channels):
            raise ValueError(f"Expected {len(channels)} values, got {len(states)}")

    def _read_uint32(self, address : int) -> int:
        return self._prot.read_multi_register_value(address, 2, word_order=self.WORD_ORDER).to_uint()

    def _write_uint32(self, address : int, value : int) -> None:
        self._prot.write_multi_register_value(address,
            ModbusMultiRegisterValue.from_uint(int(value), 2, word_order=self.WORD_ORDER))

    def _read_float(self, address : int) -> float:
        return self._prot.read_multi_register_value(address, 2, word_order=self.WORD_ORDER).to_float()

    # ┌───────────────────────────────┐
    # │ GCL (Graphic Condition Logic) │
    # └───────────────────────────────┘

    def clear_gcl_counter(self, index : int) -> None:
        """
        Reset a GCL internal counter

        Parameters
        ----------
        index : int
            0 to 7
        """
        self._check_channel(index, self.GCL_COUNTERS, "GCL counter")
        self._prot.write_single_coil(self.Coil.CLEAR_GCL_COUNTER + index, True)

    def read_gcl_flags(self) -> list[bool]:
        """
        Read the 16 GCL internal flags

        Returns
        -------
        flags : list
            One bool per flag (0 to 15)
        """
        value = self._prot.read_single_register(self.Register.GCL_FLAGS)
        return [bool(value & (1 << i)) for i in self.GCL_FLAGS]

    def write_gcl_flag(self, index : int, state : bool) -> None:
        """
        Set a GCL internal flag

        Parameters
        ----------
        index : int
            0 to 15
        state : bool
        """
        self._check_channel(index, self.GCL_FLAGS, "GCL flag")
        value = self._prot.read_single_register(self.Register.GCL_FLAGS)
        if state:
            value |= 1 << index
        else:
            value &= ~(1 << index)
        self._prot.write_single_register(self.Register.GCL_FLAGS, value)


class DigitalInputs(Adam6200):
    """
    Digital inputs (state only)
    """
    DI_CHANNELS : list[int] = []

    def read_digital_in(self, channel : int) -> bool:
        """
        Read the state of a digital input

        Parameters
        ----------
        channel : int

        Returns
        -------
        state : bool
        """
        self._check_channel(channel, self.DI_CHANNELS)
        return self._prot.read_single_coil(self.Coil.DI_VALUE + channel)

    def read_digital_ins(self) -> list[bool]:
        """
        Read the state of all digital inputs

        Returns
        -------
        states : list
            One bool per channel
        """
        return self._prot.read_coils(self.Coil.DI_VALUE, len(self.DI_CHANNELS))


class CounterInputs(DigitalInputs):
    """
    Digital inputs with latch, counter and frequency functions
    """
    # Frequency resolution (0.1 Hz)
    FREQUENCY_UNIT = 0.1

    def read_latch(self, channel : int) -> bool:
        """
        Read the latch status of a digital input (latch modes only)

        Parameters
        ----------
        channel : int

        Returns
        -------
        latched : bool
        """
        self._check_channel(channel, self.DI_CHANNELS)
        return self._prot.read_single_coil(self.Coil.DI_LATCH + channel)

    def clear_latch(self, channel : int) -> None:
        """
        Clear the latch of a digital input

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.DI_CHANNELS)
        self._prot.write_single_coil(self.Coil.DI_LATCH + channel, True)

    def start_counter(self, channel : int) -> None:
        """
        Start the counter of a digital input (counter mode only)

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.DI_CHANNELS)
        self._prot.write_single_coil(self.Coil.COUNTER_START_STOP + channel, True)

    def stop_counter(self, channel : int) -> None:
        """
        Stop the counter of a digital input

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.DI_CHANNELS)
        self._prot.write_single_coil(self.Coil.COUNTER_START_STOP + channel, False)

    def is_counter_running(self, channel : int) -> bool:
        """
        Return True if the counter of a digital input is running

        Parameters
        ----------
        channel : int

        Returns
        -------
        running : bool
        """
        self._check_channel(channel, self.DI_CHANNELS)
        return self._prot.read_single_coil(self.Coil.COUNTER_START_STOP + channel)

    def clear_counter(self, channel : int) -> None:
        """
        Reset the counter of a digital input to 0

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.DI_CHANNELS)
        self._prot.write_single_coil(self.Coil.CLEAR_COUNTER + channel, True)

    def read_counter(self, channel : int) -> int:
        """
        Read the counter value of a digital input (counter mode only)

        Parameters
        ----------
        channel : int

        Returns
        -------
        count : int
            32-bit value
        """
        self._check_channel(channel, self.DI_CHANNELS)
        return self._read_uint32(self.Register.COUNTER_FREQUENCY + 2 * channel)

    def read_frequency(self, channel : int) -> float:
        """
        Read the frequency of a digital input (frequency mode only)

        Parameters
        ----------
        channel : int

        Returns
        -------
        frequency : float
            Frequency in Hz (0.1 Hz resolution)
        """
        self._check_channel(channel, self.DI_CHANNELS)
        return self._read_uint32(self.Register.COUNTER_FREQUENCY + 2 * channel) * self.FREQUENCY_UNIT

    def read_counter_overflow(self, channel : int) -> bool:
        """
        Return True if the counter of a digital input has overflowed

        Parameters
        ----------
        channel : int

        Returns
        -------
        overflow : bool
        """
        self._check_channel(channel, self.DI_CHANNELS)
        return self._prot.read_single_coil(self.Coil.CLEAR_OVERFLOW + channel)

    def clear_counter_overflow(self, channel : int) -> None:
        """
        Clear the overflow flag of a counter

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.DI_CHANNELS)
        self._prot.write_single_coil(self.Coil.CLEAR_OVERFLOW + channel, True)


class DigitalOutputs(Adam6200):
    """
    Digital outputs with pulse output function
    """
    DO_CHANNELS : list[int] = []
    # Pulse width resolution (0.1 ms)
    PULSE_WIDTH_UNIT = 1e-4

    def write_digital_out(self, channel : int, state : bool) -> None:
        """
        Set the state of a digital output

        Parameters
        ----------
        channel : int
        state : bool
        """
        self._check_channel(channel, self.DO_CHANNELS)
        self._prot.write_single_coil(self.Coil.DO_VALUE + channel, bool(state))

    def read_digital_out(self, channel : int) -> bool:
        """
        Read the state of a digital output

        Parameters
        ----------
        channel : int

        Returns
        -------
        state : bool
        """
        self._check_channel(channel, self.DO_CHANNELS)
        return self._prot.read_single_coil(self.Coil.DO_VALUE + channel)

    def write_digital_outs(self, states : list[bool]) -> None:
        """
        Set the state of all digital outputs at once

        Parameters
        ----------
        states : list
            One bool per channel, e.g. [True, False, ...]
        """
        self._check_states(states, self.DO_CHANNELS)
        self._prot.write_multiple_coils(self.Coil.DO_VALUE, [bool(s) for s in states])

    def read_digital_outs(self) -> list[bool]:
        """
        Read the state of all digital outputs

        Returns
        -------
        states : list
            One bool per channel
        """
        return self._prot.read_coils(self.Coil.DO_VALUE, len(self.DO_CHANNELS))

    # Pulse output, the output must be set to "Pulse output" mode

    def set_pulse_width(self, channel : int, low : float, high : float) -> None:
        """
        Set the low and high durations of the pulses

        Parameters
        ----------
        channel : int
        low : float
            Low (off) duration in seconds, 0.1 ms resolution
        high : float
            High (on) duration in seconds, 0.1 ms resolution
        """
        self._check_channel(channel, self.DO_CHANNELS)
        self._write_uint32(self.Register.PULSE_LOW_WIDTH + 2 * channel, round(low / self.PULSE_WIDTH_UNIT))
        self._write_uint32(self.Register.PULSE_HIGH_WIDTH + 2 * channel, round(high / self.PULSE_WIDTH_UNIT))

    def get_pulse_width(self, channel : int) -> tuple[float, float]:
        """
        Get the low and high durations of the pulses

        Parameters
        ----------
        channel : int

        Returns
        -------
        low : float
            Low (off) duration in seconds
        high : float
            High (on) duration in seconds
        """
        self._check_channel(channel, self.DO_CHANNELS)
        low = self._read_uint32(self.Register.PULSE_LOW_WIDTH + 2 * channel)
        high = self._read_uint32(self.Register.PULSE_HIGH_WIDTH + 2 * channel)
        return low * self.PULSE_WIDTH_UNIT, high * self.PULSE_WIDTH_UNIT

    def generate_pulses(self, channel : int, count : int) -> None:
        """
        Generate a number of pulses

        Parameters
        ----------
        channel : int
        count : int
            Number of pulses
        """
        self._check_channel(channel, self.DO_CHANNELS)
        self._write_uint32(self.Register.ABSOLUTE_PULSE + 2 * channel, count)

    def add_pulses(self, channel : int, count : int) -> None:
        """
        Add pulses to the ones currently being generated

        Parameters
        ----------
        channel : int
        count : int
            Number of pulses to add
        """
        self._check_channel(channel, self.DO_CHANNELS)
        self._write_uint32(self.Register.INCREMENTAL_PULSE + 2 * channel, count)


class RelayOutputs(DigitalOutputs):
    """
    Relay outputs, same as digital outputs with relay names

    Relays are slow (8 ms set/reset time) and have a limited lifetime, keep that in mind
    when using the pulse output function
    """

    def write_relay(self, channel : int, state : bool) -> None:
        """
        Set the state of a relay

        Parameters
        ----------
        channel : int
        state : bool
            True : relay on (NO contact closed), False : relay off
        """
        self.write_digital_out(channel, state)

    def read_relay(self, channel : int) -> bool:
        """
        Read the state of a relay

        Parameters
        ----------
        channel : int

        Returns
        -------
        state : bool
        """
        return self.read_digital_out(channel)

    def write_relays(self, states : list[bool]) -> None:
        """
        Set the state of all relays at once

        Parameters
        ----------
        states : list
            One bool per channel, e.g. [True, False, ...]
        """
        self.write_digital_outs(states)

    def read_relays(self) -> list[bool]:
        """
        Read the state of all relays

        Returns
        -------
        states : list
            One bool per channel
        """
        return self.read_digital_outs()
