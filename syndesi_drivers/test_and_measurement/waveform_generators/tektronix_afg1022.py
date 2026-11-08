from enum import Enum
from syndesi import SCPI, Visa, Adapter

class Function(Enum):
    """
    Arbitrary waveform generator function
    """
    SINUSOID = 'SIN'
    SQUARE = 'SQU'
    RAMP = 'RAMP'
    PULSE = 'PULS'
    PRNOISE = 'PRN'
    DC = 'DC'
    ARBITRARY = 'EFIL'

class Unit(Enum):
    VPP = 'VPP'
    VRMS = 'VRMS'
    DBM = 'DBM'

HIGH_IMPEDANCE_KEYWORD = 'HIGH'

class AFG1022:
    """
    Tektronix AFG1022 Arbitrary waveform generator

    Parameters
    ----------
    adpater : Adapter
    """
    def __init__(self, adapter: Adapter) -> None:
        super().__init__()

        assert isinstance(adapter, Visa), "Invalid adapter"
        self._prot = SCPI(adapter, '\n')

    def test(self) -> bool:
        """
        Test presence of the device

        Returns
        -------
        True if the device is present
        False if the device doesn't respond or it is the wrong device
        """
        output = self._prot.query('*IDN?')
        # Output is typically :
        # TEKTRONIX,AFG1022,1703954,SCPI:99.0 FC:V1.2.1b
        return "AFG1022" in output

    def _check_channel(self, channel : int) -> None:
        """
        Check the channel type and value
        """
        assert isinstance(channel, int), f"Invalid channel type : {type(channel)}"
        assert 1 <= channel <= 2, f"Invalid channel value : {channel}"

    def set_output_state(self, channel : int, state : bool) -> None:
        """
        Set the output state for the desired channel
        
        Parameters
        ----------
        channel : int
        state : bool
        """
        self._check_channel(channel)
        self._prot.write(f'OUTP{channel} {"ON" if state else "OFF"}')

    def set_frequency_sync(self, source_channel : int, state : bool) -> None:
        """
        Enable or disable frequency sync (concurrent mode),
        the specified source_channel's frequency is copied on the other one

        Parameters
        ----------
        source_channel : int
        state : bool
        """
        self._check_channel(source_channel)
        self._prot.write(f'SOUR{source_channel}:FREQ_CONC {"ON" if state else "OFF"}')

    def set_frequency(self, channel : int, frequency : float) -> None:
        """
        Sets the frequency of output waveform for the specified
        channel.
        This command is available when the Run Mode is set to other than Sweep.

        Parameters
        ----------
        channel : int
        frequency : float
        """
        self._check_channel(channel)
        self._prot.write(f'SOUR{int(channel)}:FREQ {float(frequency):.6f}')

    def set_function(self,
                     channel : int,
                     function : Function,
                     duty_cycle : float | None = None,
                     name : str | None = None) -> None:
        """
        Set the waveform function for the desired channel

        Parameters
        ----------
        function : Function
        channel : int
        duty_cycle : float
            Duty-cycle in percent (pulse mode only)
        name : str
            For user mode only, name of waveform file or 'VOLATILE'
        """
        self._check_channel(channel)
        assert isinstance(function, Function), f"Invalid function type : {type(function)}"
        # TODO : Add built-ins
        if function == Function.ARBITRARY:
            if name is not None:
                self._prot.write(f'SOUR{channel}:FUNC EFIL {name}')
            else:
                raise ValueError("waveform name cannot be None")
        else:
            self._prot.write(f'SOUR{channel}:FUNC {function.value}')

        if function == Function.PULSE and duty_cycle is not None:
            self._prot.write(f'SOUR{channel}:PULS:DCYC {duty_cycle}')

    def set_phase(self, channel : int, phase : float, degrees : bool = False) -> None:
        """
        Set the phase of the desired channel

        Parameters
        ----------
        channel : int
        phase : float
        degrees : bool
            True : use degrees
            False (default) : use radians
        """
        self._check_channel(channel)
        self._prot.write(f'SOUR{channel}:PHAS {float(phase):.6f}{"DEG" if degrees else "RAD"}')

    def set_amplitude_offset(self, channel : int, amplitude : float, offset : float) -> None:
        """
        Set the amplitude and offset voltage for the desired channel

        Parameters
        ----------
        channel : int
        amplitude : float
        offset : float
        """
        self._check_channel(channel)
        # Set low voltage
        self._prot.write(f'SOUR{channel}:VOLT:AMPL {float(amplitude):.3f}')
        self._prot.write(f'SOUR{channel}:VOLT:OFFS {float(offset):.3f}')

    def set_low_high(self, channel : int, low : float, high : float) -> None:
        """
        Set the low and high voltage values for the desired channel

        Parameters
        ----------
        channel : int
        low : float
        high : float
        """
        self._check_channel(channel)
        assert high >= low, f'Invalid low-high combination : {low}, {high}'
        self.set_amplitude_offset(channel, high - low, (low + high) / 2)

    def set_output_load(self, channel : int, load : str | float) -> None:
        """
        Set the output load for the desired channel

        Parameters
        ----------
        channel : int
        load : str, float
            'HIGH' for high impedance
            float value for anything else
        """
        self._check_channel(channel)

        if isinstance(load, str) and load.upper() == HIGH_IMPEDANCE_KEYWORD:
            argument = 'INF'
        else:
            argument = f"{float(load):.3f}"

        self._prot.write(f'OUTP{channel}:IMP {argument}')
