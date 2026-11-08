# File : iologik_e1200.py
# Author : Sébastien Deriaz
# License : GPL
"""
Common base for the MOXA ioLogik E1200 series (Modbus TCP IO modules)

Each module declares its own Modbus map (ioLogik E1200 User's Manual, appendix A) in
up to four enums, one per Modbus table :
- Coil : coils (0X, function codes 01, 05, 0F)
- DiscreteInput : discrete inputs (1X, function code 02)
- InputRegister : input registers (3X, function code 04)
- HoldingRegister : holding registers (4X, function codes 03, 06, 10)

The tables are separate, the same number can be used in several of them.
Addresses are taken from the "Start Register" column of the manual with the table prefix
dropped : 30017 -> 17, 41025 -> 1025

Channel modes (DI / counter, DO / pulse, sensor types, scaling, ...) are configured with
the web console
"""

from enum import IntEnum
from typing import Any

from syndesi import IP, Driver, Modbus
from syndesi.protocols.modbus import Endian, ModbusMultiRegisterValue

class IoLogikE1200(Driver):
    # 32-bit values are stored high word first
    WORD_ORDER = Endian.BIG
    # Modbus map, defined by each module
    Coil : Any
    DiscreteInput : Any
    InputRegister : Any
    HoldingRegister : Any

    # System information, same for every module (input registers)
    class System(IntEnum):
        MODEL_NAME = 5001
        UPTIME = 5021
        MAC_ADDRESS = 5025
        IP_ADDRESS = 5028
        FIRMWARE_VERSION = 5030
        DEVICE_NAME = 5041

    def __init__(self, adapter : IP) -> None:
        """
        ioLogik E1200 module

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
            return self.get_model_name().startswith("E12")
        except Exception:
            return False

    def _check_channel(self, channel : int, channels : list[int]) -> None:
        if channel not in channels:
            raise ValueError(f"Invalid channel : {channel}, must be in {channels}")

    def _check_states(self, states : list[bool], channels : list[int]) -> None:
        if len(states) != len(channels):
            raise ValueError(f"Expected {len(channels)} values, got {len(states)}")

    def _read_input_value(self, address : int, n_registers : int) -> ModbusMultiRegisterValue:
        registers = self._prot.read_input_registers(address, n_registers)
        return ModbusMultiRegisterValue.from_registers(registers, Endian.BIG, self.WORD_ORDER)

    def _read_input_uint32(self, address : int) -> int:
        return self._read_input_value(address, 2).to_uint()

    def _read_input_float(self, address : int) -> float:
        return self._read_input_value(address, 2).to_float()

    def _read_input_bytes(self, address : int, n_registers : int) -> bytes:
        return self._read_input_value(address, n_registers).to_array()

    # ┌────────┐
    # │ System │
    # └────────┘

    def get_model_name(self) -> str:
        """
        Return the model name, e.g. "E1214"

        Returns
        -------
        name : str
        """
        return self._read_input_bytes(self.System.MODEL_NAME, 10).decode("ascii", "ignore").strip("\x00 ")

    def get_device_name(self) -> str:
        """
        Return the device name (set in the web console)

        Returns
        -------
        name : str
        """
        return self._read_input_bytes(self.System.DEVICE_NAME, 30).decode("ascii", "ignore").strip("\x00 ")

    def get_firmware_version(self) -> str:
        """
        Return the firmware version, e.g. "V1.2.3"

        Returns
        -------
        version : str
        """
        data = self._read_input_bytes(self.System.FIRMWARE_VERSION, 2)
        return f"V{data[0]}.{data[1]}.{data[2]}"

    def get_uptime(self) -> int:
        """
        Return the time since power up

        Returns
        -------
        uptime : int
            Uptime in seconds
        """
        return self._read_input_uint32(self.System.UPTIME)

    def get_ip_address(self) -> str:
        """
        Return the IP address, e.g. "192.168.127.254"

        Returns
        -------
        address : str
        """
        return ".".join(str(b) for b in self._read_input_bytes(self.System.IP_ADDRESS, 2))

    def get_mac_address(self) -> str:
        """
        Return the MAC address, e.g. "00:90:E8:3E:18:CC"

        Returns
        -------
        address : str
        """
        return ":".join(f"{b:02X}" for b in self._read_input_bytes(self.System.MAC_ADDRESS, 3))


class Watchdog(IoLogikE1200):
    """
    Communication watchdog of the output modules

    When enabled in the web console, the outputs go to their safe state if the
    communication is lost for too long
    """

    def clear_watchdog_alarm(self) -> None:
        """
        Clear the watchdog alarm (leave safe mode)
        """
        self._prot.write_single_coil(self.Coil.WATCHDOG_ALARM, True)


class DigitalInputs(IoLogikE1200):
    """
    Digital inputs with counter function
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
        return self._prot.read_discrete_inputs(self.DiscreteInput.DI_STATUS + channel, 1)[0]

    def read_digital_ins(self) -> list[bool]:
        """
        Read the state of all digital inputs

        Returns
        -------
        states : list
            One bool per channel
        """
        return self._prot.read_discrete_inputs(self.DiscreteInput.DI_STATUS, len(self.DI_CHANNELS))

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

    def reset_counter(self, channel : int) -> None:
        """
        Reset the counter of a digital input to its initial value

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.DI_CHANNELS)
        self._prot.write_single_coil(self.Coil.COUNTER_RESET + channel, True)

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
        return self._read_input_uint32(self.InputRegister.COUNTER_VALUE + 2 * channel)

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
        return self._prot.read_discrete_inputs(self.DiscreteInput.COUNTER_OVERFLOW + channel, 1)[0]

    def clear_counter_overflow(self, channel : int) -> None:
        """
        Clear the overflow flag of a counter

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.DI_CHANNELS)
        self._prot.write_single_coil(self.Coil.COUNTER_OVERFLOW_CLEAR + channel, True)


class DigitalOutputs(Watchdog):
    """
    Digital outputs with pulse output function
    """
    DO_CHANNELS : list[int] = []
    # Pulse width resolution (1 ms)
    PULSE_WIDTH_UNIT = 1e-3
    # Number of registers used by each pulse count
    PULSE_COUNT_SIZE = 1

    def write_digital_out(self, channel : int, state : bool) -> None:
        """
        Set the state of a digital output

        Parameters
        ----------
        channel : int
        state : bool
        """
        self._check_channel(channel, self.DO_CHANNELS)
        self._prot.write_single_coil(self.Coil.DO_STATUS + channel, bool(state))

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
        return self._prot.read_single_coil(self.Coil.DO_STATUS + channel)

    def write_digital_outs(self, states : list[bool]) -> None:
        """
        Set the state of all digital outputs at once

        Parameters
        ----------
        states : list
            One bool per channel, e.g. [True, False, ...]
        """
        self._check_states(states, self.DO_CHANNELS)
        self._prot.write_multiple_coils(self.Coil.DO_STATUS, [bool(s) for s in states])

    def read_digital_outs(self) -> list[bool]:
        """
        Read the state of all digital outputs

        Returns
        -------
        states : list
            One bool per channel
        """
        return self._prot.read_coils(self.Coil.DO_STATUS, len(self.DO_CHANNELS))

    # Pulse output, the output must be set to "Pulse output" mode

    def set_pulse_width(self, channel : int, on : float, off : float) -> None:
        """
        Set the on and off durations of the pulses

        Parameters
        ----------
        channel : int
        on : float
            On duration in seconds
        off : float
            Off duration in seconds
        """
        self._check_channel(channel, self.DO_CHANNELS)
        self._prot.write_single_register(self.HoldingRegister.PULSE_ON_WIDTH + channel, round(on / self.PULSE_WIDTH_UNIT))
        self._prot.write_single_register(self.HoldingRegister.PULSE_OFF_WIDTH + channel, round(off / self.PULSE_WIDTH_UNIT))

    def get_pulse_width(self, channel : int) -> tuple[float, float]:
        """
        Get the on and off durations of the pulses

        Parameters
        ----------
        channel : int

        Returns
        -------
        on : float
            On duration in seconds
        off : float
            Off duration in seconds
        """
        self._check_channel(channel, self.DO_CHANNELS)
        on = self._prot.read_single_register(self.HoldingRegister.PULSE_ON_WIDTH + channel)
        off = self._prot.read_single_register(self.HoldingRegister.PULSE_OFF_WIDTH + channel)
        return on * self.PULSE_WIDTH_UNIT, off * self.PULSE_WIDTH_UNIT

    def set_pulse_count(self, channel : int, count : int) -> None:
        """
        Set the number of pulses generated when the pulse output is started

        Parameters
        ----------
        channel : int
        count : int
        """
        self._check_channel(channel, self.DO_CHANNELS)
        address = self.HoldingRegister.PULSE_COUNT + self.PULSE_COUNT_SIZE * channel
        self._prot.write_multi_register_value(address,
            ModbusMultiRegisterValue.from_uint(int(count), self.PULSE_COUNT_SIZE, word_order=self.WORD_ORDER))

    def get_pulse_count(self, channel : int) -> int:
        """
        Get the number of pulses generated when the pulse output is started

        Parameters
        ----------
        channel : int

        Returns
        -------
        count : int
        """
        self._check_channel(channel, self.DO_CHANNELS)
        address = self.HoldingRegister.PULSE_COUNT + self.PULSE_COUNT_SIZE * channel
        return self._prot.read_multi_register_value(address, self.PULSE_COUNT_SIZE, word_order=self.WORD_ORDER).to_uint()

    def start_pulse(self, channel : int) -> None:
        """
        Start the pulse output

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.DO_CHANNELS)
        self._prot.write_single_coil(self.Coil.PULSE_START_STOP + channel, True)

    def stop_pulse(self, channel : int) -> None:
        """
        Stop the pulse output

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.DO_CHANNELS)
        self._prot.write_single_coil(self.Coil.PULSE_START_STOP + channel, False)

    def is_pulse_running(self, channel : int) -> bool:
        """
        Return True if the pulse output is running

        Parameters
        ----------
        channel : int

        Returns
        -------
        running : bool
        """
        self._check_channel(channel, self.DO_CHANNELS)
        return self._prot.read_single_coil(self.Coil.PULSE_START_STOP + channel)


class RelayOutputs(DigitalOutputs):
    """
    Relay outputs, same as digital outputs with relay names and switching counters
    """

    def write_relay(self, channel : int, state : bool) -> None:
        """
        Set the state of a relay

        Parameters
        ----------
        channel : int
        state : bool
            True : relay on, False : relay off
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

    def read_relay_total_count(self, channel : int) -> int:
        """
        Read the total number of switching operations of a relay (lifetime)

        Parameters
        ----------
        channel : int

        Returns
        -------
        count : int
        """
        self._check_channel(channel, self.DO_CHANNELS)
        return self._read_input_uint32(self.InputRegister.RELAY_TOTAL_COUNT + 2 * channel)

    def read_relay_count(self, channel : int) -> int:
        """
        Read the number of switching operations of a relay since the last reset

        Parameters
        ----------
        channel : int

        Returns
        -------
        count : int
        """
        self._check_channel(channel, self.DO_CHANNELS)
        return self._read_input_uint32(self.InputRegister.RELAY_CURRENT_COUNT + 2 * channel)

    def reset_relay_count(self, channel : int) -> None:
        """
        Reset the switching counter of a relay (the total count is kept)

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.DO_CHANNELS)
        self._prot.write_single_coil(self.Coil.RELAY_COUNT_RESET + channel, True)


class AnalogInputs(IoLogikE1200):
    """
    Analog inputs (voltage, current, RTD or thermocouple) with min/max values

    The values are the "scaled" values : engineering units, or the unit defined by the
    scaling function of the web console if it is enabled
    """
    AI_CHANNELS : list[int] = []

    def read_analog_in(self, channel : int) -> float:
        """
        Read the value of an analog input

        Parameters
        ----------
        channel : int

        Returns
        -------
        value : float
        """
        self._check_channel(channel, self.AI_CHANNELS)
        return self._read_input_float(self.InputRegister.AI_VALUE + 2 * channel)

    def read_max(self, channel : int) -> float:
        """
        Read the maximum value of an analog input since the last reset

        Parameters
        ----------
        channel : int

        Returns
        -------
        value : float
        """
        self._check_channel(channel, self.AI_CHANNELS)
        return self._read_input_float(self.InputRegister.AI_MAX + 2 * channel)

    def read_min(self, channel : int) -> float:
        """
        Read the minimum value of an analog input since the last reset

        Parameters
        ----------
        channel : int

        Returns
        -------
        value : float
        """
        self._check_channel(channel, self.AI_CHANNELS)
        return self._read_input_float(self.InputRegister.AI_MIN + 2 * channel)

    def reset_max(self, channel : int) -> None:
        """
        Reset the maximum value of an analog input

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.AI_CHANNELS)
        self._prot.write_single_coil(self.Coil.RESET_MAX + channel, True)

    def reset_min(self, channel : int) -> None:
        """
        Reset the minimum value of an analog input

        Parameters
        ----------
        channel : int
        """
        self._check_channel(channel, self.AI_CHANNELS)
        self._prot.write_single_coil(self.Coil.RESET_MIN + channel, True)


class VoltageCurrentInputs(AnalogInputs):
    """
    Voltage / current analog inputs with mode and status

    Voltage or current is also selected with a jumper inside the module
    """

    class Mode(IntEnum):
        V_0_10 = 0              # 0 to 10 V
        MA_4_20 = 1             # 4 to 20 mA
        MA_0_20 = 2             # 0 to 20 mA
        MA_4_20_BURNOUT = 4     # 4 to 20 mA with burnout detection

    class Status(IntEnum):
        NORMAL = 0
        BURNOUT = 1
        OVER_RANGE = 2
        UNDER_RANGE = 3

    def set_mode(self, channel : int, mode : Mode) -> None:
        """
        Set the input mode of an analog input

        Parameters
        ----------
        channel : int
        mode : Mode
            e.g. Mode.MA_4_20
        """
        self._check_channel(channel, self.AI_CHANNELS)
        self._prot.write_single_register(self.HoldingRegister.AI_MODE + channel, self.Mode(mode))

    def get_mode(self, channel : int) -> Mode:
        """
        Get the input mode of an analog input

        Parameters
        ----------
        channel : int

        Returns
        -------
        mode : Mode
        """
        self._check_channel(channel, self.AI_CHANNELS)
        return self.Mode(self._prot.read_single_register(self.HoldingRegister.AI_MODE + channel))

    def read_status(self, channel : int) -> Status:
        """
        Read the status of an analog input

        Parameters
        ----------
        channel : int

        Returns
        -------
        status : Status
            NORMAL, BURNOUT, OVER_RANGE or UNDER_RANGE
        """
        self._check_channel(channel, self.AI_CHANNELS)
        return self.Status(self._prot.read_input_registers(self.InputRegister.AI_STATUS + channel, 1)[0])


class TemperatureInputs(AnalogInputs):
    """
    RTD or thermocouple inputs, the sensor type is selected in the web console
    """

    def read_temperature(self, channel : int) -> float:
        """
        Read the temperature of an input

        Parameters
        ----------
        channel : int

        Returns
        -------
        temperature : float
            Temperature in °C or °F (or ohm / mV if the input is in resistance / voltage mode)
        """
        return self.read_analog_in(channel)
