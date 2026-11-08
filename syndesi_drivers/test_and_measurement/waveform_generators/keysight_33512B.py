from enum import StrEnum
from syndesi import IP, Visa, SCPI, SubDriver

from syndesi_drivers.tools import NormalizedStrEnum
from ..instrument import MultiChannelInstrument

# https://www.keysight.com/fr/en/assets/9018-03714/service-manuals/9018-03714.pdf?success=true

class WaveformFunction(NormalizedStrEnum):
    """Waveform function"""
    SIN = 'SIN'
    SQU = 'SQU'
    TRI = 'TRI'
    RAMP = 'RAMP'
    PULS = 'PULS'
    PRBS = 'PRBS'
    ARB = 'ARB'
    DC = 'DC'

class VoltUnit(NormalizedStrEnum):
    """Volt unit"""
    VPP = 'VPP'
    VRMS = 'VRMS'
    DBM = 'DBM'

class AngleUnit(NormalizedStrEnum):
    """Angle unit"""
    DEG = 'DEG'
    RAD = 'RAD'
    SEC = 'SEC'

HIGH_IMPEDANCE_KEYWORD = "HIGH"


class Keysight33512BChannel(SubDriver):
    """
    A single Keysight 33512B channel
    """
    def __init__(self, protocol : SCPI, channel : int) -> None:
        self._prot = protocol
        self._channel = channel

    def set_waveform_function(self, waveform : str):
        """
        Sets the waveform shape of the specified channel, available values are :
            - SIN : Sinusoisdal
            - SQU : Square
            - TRI : Triangle
            - RAMP : Ramp
            - PULS : Pulse
            - PRBS : Pseudo-random noise using LFSR
            - ARB : Arbitrary waveform
            - DC : Constant

        Parameters
        ----------
        waveform : str
        """
        waveform = WaveformFunction(waveform)

        self._prot.write(f'SOUR{self._channel}:FUNC {waveform.value}')

    def set_arbitrary_file(self, filename : str):
        """
        Selects an arbitrary waveform (.arb/.barb) or sequence (.seq) that has
        previously been loaded into volatile memory for the channel specified
        with load_arbitrary_waveform or load_memory_to_volatile

        Parameters
        ----------
        filename : str
        """
        self._prot.write(f'SOUR{self._channel}:FUNC:ARB {filename}')

    def set_frequency(self, frequency : float):
        """
        Sets the frequency of the specified channel

        Parameters
        ----------
        frequency : float
        """
        assert isinstance(frequency, float) or isinstance(frequency, int), f"Invalid frequency type : {type(frequency)}"
        self._prot.write(f'SOUR{self._channel}:FREQ {frequency}')

    def set_dc_value(self, value : float, unit : str | None = None):
        """
        Set the DC voltage value
        Parameters
        ----------
        value : float
        unit : str
            VPP, VRMS or DBM
        """
        if unit is not None:
            self._prot.write(f'SOUR{self._channel}:VOLT:UNIT {VoltUnit(unit).value}')
        self._prot.write(f'SOUR{self._channel}:VOLT:OFFS {value:.6f}')

    def set_amplitude_offset(self, amplitude : float, offset : float, unit : str | None = None):
        """
        Sets the amplitude and offset of the specified channel

        Cannot be used for setting DC value, use .set_dc_value(channel, value)

        Parameters
        ----------
        amplitude : float
        offset : float
        unit : str
            VPP, VRMS or DBM
        """
        if unit is not None:
            self._prot.write(f'SOUR{self._channel}:VOLT:UNIT {VoltUnit(unit).value}')

        self._prot.write(f'SOUR{self._channel}:VOLT:OFFS {offset:.6f}')
        self._prot.write(f'SOUR{self._channel}:VOLT {amplitude:.6f}')

    def set_low_high(self, low : float, high : float, unit : str | None = None):
        """
        Sets the high and low voltage values of the specified channel

        Parameters
        ----------
        high : float
        low : float
        unit : str
            VPP, VRMS or DBM
        """
        if unit is not None:
            self._prot.write(f'SOUR{self._channel}:VOLT:UNIT {VoltUnit(unit).value}')
        if low >= high:
            raise ValueError("low value cannot be lower or equal than high value")
        self._prot.write(f'SOUR{self._channel}:VOLT:LOW {low:.6f}')
        self._prot.write(f'SOUR{self._channel}:VOLT:HIGH {high:.6f}')

    def set_output_load(self, load : str | int | float):
        """
        Sets the output impedance of the specified channel

        Parameters
        ----------
        load : float/str
            Value or 'high'
        """
        if isinstance(load, str) and load.upper() == HIGH_IMPEDANCE_KEYWORD.upper():
            # Set high impedance
            self._prot.write(f'OUTP{self._channel}:LOAD INF')
        else:
            self._prot.write(f'OUTP{self._channel}:LOAD {load:.6f}')

    def set_output_state(self, state : bool):
        """
        Sets the output state of the desired channel
        
        Parameters
        ----------
        state : bool
        """
        assert isinstance(state, bool) or isinstance(state, int), f"Invalid state type : {type(state)}"
        self._prot.write(f'OUTP{self._channel} {"ON" if state else "OFF"}')

    def set_phase(self, phase : float, unit : str | None = None):
        """
        Sets the phase of the specified channel
        
        Parameters
        ----------
        phase : float
        unit : str
            DEG, RAD or SEC (seconds), default to 'DEG'
        """
        if unit is not None:
            self._prot.write(f'UNIT:ANGL {AngleUnit(unit).value}')
        self._prot.write(f'SOUR{self._channel}:PHAS {phase:.6f}')

    def get_current_waveform_function(self) -> WaveformFunction:
        """
        Return the current waveform function of the specified channel
        """
        output = self._prot.query(f'SOUR{self._channel}:FUNC?')
        return WaveformFunction(output)

    def set_duty_cycle(self, duty_cycle : float):
        """
        Sets the duty cycle of the specified channel (square and pulse only)

        Parameters
        ----------
        duty_cycle : float
            Percent
        """
        if not (0 <= duty_cycle <= 100):
            raise ValueError(f"Invalid duty_cycle value {duty_cycle}")
        func = self.get_current_waveform_function()
        if func not in [WaveformFunction.SQU or WaveformFunction.PULS]:
            raise ValueError("Cannot set duty_cycle when not in square or pulse mode")
        self._prot.write(f'SOUR{self._channel}:FUNC:{func}:DCYCLE {duty_cycle}')

    def set_autorange(self, state : bool):
        """
        Enable or disable autoranging on the specified channel
        To set a desired range
        - set the output state to False
        - enable autoranging
        - configure the maximum voltage range
        - disable autoranging
        Parameters
        ----------
        state : bool
        """
        self._prot.write(f'SOUR{self._channel}:VOLT:RANG:AUTO {"ON" if state else "OFF"}')

    def get_volatile_catalog(self) -> list[str]:
        """
        Returns the contents of volatile waveform memory, including arbitrary
        waveforms and sequences for the specified channel
        """
        # Output like : '"EXP_RISE","TEST"'
        output = self._prot.query(f'SOUR{self._channel}:DATA:VOL:CAT?')
        catalog = []
        if ',' in output:
            catalog += [x.replace('"', '') for x in output.split(',')]
        return catalog

    def clear_volatile_memory(self):
        """
        Clears waveform memory for the specified channel and reloads the default waveform.
        """
        self._prot.write(f'SOUR{self._channel}:DATA:VOL:CLE')

    def load_arbitrary_waveform(self, name : str, points : list, dac=False, overwrite=False):
        """
        Downloads integer values representing DAC codes between -32768 and +32767(dac=True)
        or floating point values (dac=False) into waveform volatile memory
        Load an arbitrary waveform in memory

        Call load_from_memory()

        Parameters
        ----------
        name : str
            Name of the arbitrary waveform
        points : list or np.array
        dac : bool
            True : points are raw DAC values (-32768 to 32767)
            False (default) : points are -1.0 to +1.0
        overwrite : bool
            Overwrite existing file
        """
        # Check if the file already exists (all names are uppercased)
        if name.upper() in self.get_volatile_catalog():
            if overwrite:
                self.clear_volatile_memory()
            else:
                raise RuntimeError(f"File {name} already exists. To ignore, set overwrite=True")

        RANGE = (-32767, 32767) if dac else (-1.0, 1.0)
        assert min(points) >= RANGE[0] and max(points) <= RANGE[1], f"Invalid points range ({min(points)} to {max(points)})"
        command = f'SOUR{self._channel}:DATA:ARB'
        if dac:
            command += ':DAC'
            points_list = [f'{p:.0f}' for p in points]
        else:
            points_list = [f'{p}' for p in points]
        command += f' {name},{",".join(points_list)}'
        self._prot.write(command)

    def load_memory_to_volatile(self, path : str):
        """
        Loads the specified arb segment(.arb/.barb) or arb sequence (.seq) file in INTERNAL or USB memory into
        volatile memory for the specified channel.

        Parameters
        ----------
        path : str
        """
        self._prot.write(f'MMEM:LOAD:DATA{self._channel} \"{path}\"')


    def set_burst_state(self, state : bool, mode : str = 'triggered', n_cycles : int = 1, start_phase : float = 0, burst_period : float = None):
        """
        Enables or disables burst mode.

        Output phase is set to 0 when burst is enabled.

        Set the trigger source with set_trigger_source

        Parameters
        ----------
        state : bool
        mode : str
            'triggered' or 'gated'
        n_cycles : int
            Number of cycles
        """
        self._prot.write(f'SOUR{self._channel}:BURS:STAT {1 if state else 0}')
        if state:
            assert mode in ['triggered', 'gated'], f"Invalid mode : {mode}"
            self._prot.write(f'SOUR{self._channel}:BURS:MODE {mode}')
            self._prot.write(f'SOUR{self._channel}:BURS:NCYC {n_cycles}')
            self._prot.write(f'SOUR{self._channel}:BURS:PHAS {start_phase}')
            if burst_period is not None:
                self._prot.write(f'SOUR{self._channel}:BURS:INT:PER {burst_period}')

    def set_trigger_source(self, source : str):
        """
        Selects the trigger source for sequence, list, burst or sweep. The instrument accepts an immediate or
        timed internal trigger, an external hardware trigger from the rear-panel Ext Trig connector, or a software
        (bus) trigger.
        
        Parameters
        ----------
        source : str
            'immediate', 'external', 'timer' or 'bus'
        """
        assert source in ['immediate', 'external', 'timer', 'bus']
        self._prot.write(f'TRIG{self._channel}:SOUR {source}')

    def set_arbitrary_sample_rate(self, sample_rate : float):
        """
        Sets the sample rate for the arbitrary waveform.

        Parameters
        ----------
        sample_rate : float
        """
        self._prot.write(f'SOUR{self._channel}:FUNC:ARB:SRAT {sample_rate}')

class Keysight33512B(MultiChannelInstrument[Keysight33512BChannel]):
    """
    Keysight 33500B Trueform Series Waveform Generator

    Parameters
    ----------
    adpater : Adapter
    """
    def __init__(self, adapter: IP) -> None:
        assert isinstance(adapter, IP) or isinstance(adapter, Visa), "Invalid adapter"
        self._prot = SCPI(adapter, "\n")
        super().__init__(
            lambda channel : Keysight33512BChannel(self._prot, channel),
            [1, 2]
        )

    def set_frequency_coupling(self, enabled : bool, ratio=None, offset=None) -> None:
        """
        Sets the frequency coupling mode

        Set either ratio or offset, not both

        Parameters
        ----------
        enabled : bool
        ratio : float
        offset : float
        """
        if enabled:
            self._prot.write('FREQ:COUP ON')
            if ratio is None and offset is None:
                raise ValueError("offset and ratio cannot be both None")
            elif ratio is not None and offset is not None:
                raise ValueError("offset and ratio cannot be set at the same time")
            elif ratio is not None:
                # Set the ratio
                assert isinstance(ratio, int) or isinstance(ratio, float), f"Invalid ratio type : {type(ratio)}"
                self._prot.write('FREQ:COUP:MODE RAT')
                self._prot.write(f'FREQ:COUP:RAT {ratio}')
            else:
                # Set the offset
                assert isinstance(offset, int) or isinstance(offset, float), f"Invalid offset type : {type(offset)}"
                self._prot.write('FREQ:COUP:MODE OFFS')
                self._prot.write(f'FREQ:COUP:OFFS {offset}')
        else:
            self._prot.write('FREQ:COUP OFF')
            raise ValueError("Set either")

    def sync_phases(self):
        """
        Syncs the two channels phases, this does not change the phase values
        """
        self._prot.write('PHAS:SYNC')

    def test(self):
        """
        Test presence of the device

        Returns
        -------
        success : bool
        """
        output = self._prot.query('*IDN?')
        return '33512B' in output

    def sync_phase(self):
        """
        Simultaneously resets all phase generators in the instrument, including the modulation phase
        generators, to establish a common, internal phase zero reference point. This command does not affect
        PHASe setting of either channel; it simply establishes phase difference between channels as the sum of
        channel 1 and channel 2 sources.
        """
        self._prot.write('PHAS:SYNC')
