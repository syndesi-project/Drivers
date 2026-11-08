from enum import Enum, StrEnum
from syndesi import IP, Visa, Adapter, SCPI, Driver, SubDriver

class Function(StrEnum):
    """Function"""
    SINUSOID = 'SIN'
    SQUARE = 'SQU'
    TRIANGLE = 'TRI'
    RAMP = 'RAMP'
    PULSE = 'PULS'
    NOISE = 'NOIS'
    PRBS = 'PRBS'
    DC = 'DC'
    ARBITRARY = 'ARB'

class Unit(StrEnum):
    """Unit"""
    VPP = 'Vpp'
    VRMS = 'Vrms'
    DBM = 'dBm'

class SyncMode(StrEnum):
    """SyncMode"""
    NORMAL = 'NORM'
    CARRIER = 'CARR'
    MARKER = 'MARK'

class Polarity(StrEnum):
    """Polarity"""
    NORMAL = 'NORM'
    INVERTED = 'INV'

HIGH_IMPEDANCE_KEYWORD = 'HIGH'

# All functions were tested on 25.09.2023
class KeySight_EDU33212A_Channel(SubDriver):
    """
    Keysight EDU33212A arbitrary waveform generator channel

    Parameters
    ----------
    protocol : SCPI
    channel : int
    """
    CHANGELOG = {
        "1.0.0" : "Initial version"
    }

    def __init__(self, protocol : SCPI, channel : int) -> None:
        self._prot = protocol
        self._channel = channel

    def set_output_state(self, state : bool) -> None:
        """
        Set the output state for the desired channel
        
        Parameters
        ----------
        state : bool
        """
        self._prot.write(f'OUTP{self._channel} {"ON" if state else "OFF"}')

    def sync_phase(self) -> None:
        """
        Do a phase sync between CH1 and CH2
        """
        self._prot.write('PHAS:SYNC')

    def set_frequency(self, frequency : float) -> None:
        """
        Sets the frequency of output waveform for the specified
        channel.
        This command is available when the Run Mode is set to other than Sweep.
        Parameters
        ----------
        frequency : float
        """
        self._prot.write(f'SOUR{self._channel}:FREQ {float(frequency)}')

    def set_function(self,
                     function : Function,
                     duty_cycle : float | None = None) -> None:
        """
        Set the waveform function for the desired channel
        Parameters
        ----------
        function : Function
        duty_cycle : float
            Duty-cycle in percent (pulse and square modes only)
        """
        #assert isinstance(function, Function), f"Invalid function type : {type(function)}"

        self._prot.write(f'SOUR{self._channel}:FUNC {function.value}')

        if function in [Function.PULSE, Function.SQUARE] and duty_cycle is not None:
            self._prot.write(f'SOUR{self._channel}:FUNC:{function.value}:DCYC {duty_cycle}')

    def set_phase(self, phase : float, degrees : bool = False) -> None:
        """
        Set the phase of the desired channel
        Parameters
        ----------
        phase : float
        degrees : bool
            True : use degrees
            False (default) : use radians
        """
        self._prot.write(f'SOUR{self._channel}:PHAS {float(phase)}{"DEG" if degrees else "RAD"}')

    def set_amplitude_offset(self, amplitude : float, offset : float, unit : Unit = Unit.VPP) -> None:
        """
        Set the amplitude and offset voltage for the desired channel
        Parameters
        ----------
        amplitude : float
        offset : float
        unit : Unit
            Volts unit, Vpp by default
        """
        # Set low voltage
        self._prot.write(f'SOUR{self._channel}:VOLT:AMPL {float(amplitude)}{unit.value}')
        self._prot.write(f'SOUR{self._channel}:VOLT:OFFS {float(offset)}')

    def set_low_high(self, low : float, high : float, unit : Unit = Unit.VPP) -> None:
        """
        Set the low and high voltage values for the desired channel
        Parameters
        ----------
        low : float
        high : float
        unit : Unit
            Volts unit, Vpp by default
        """
        assert high >= low, f'Invalid low-high combination : {low}, {high}'
        self.set_amplitude_offset(high - low, (low + high) / 2, unit=unit)

    def set_output_load(self, load : str | int | float) -> None:
        """
        Sets the output impedance of the specified channel
        Parameters
        ----------
        load : int | float | str
            Value or HIGH
        """
        if isinstance(load, str) and load.upper() == 'HIGH':
            # Set high impedance
            self._prot.write(f'OUTP{self._channel}:LOAD INF')
        else:
            assert isinstance(load, float) or isinstance(load, int), f"Invalid load type : {type(load)}"
            self._prot.write(f'OUTP{self._channel}:LOAD {load}')


class EDU33212A(Driver):
    """
    Keysight EDU33212A arbitrary waveform generator
    Parameters
    ----------
    adpater : Adapter
    """
    def __init__(self, adapter: Adapter) -> None:
        super().__init__()

        assert isinstance(adapter, (Visa, IP)), "Invalid adapter"
        self._prot = SCPI(adapter, '\n')

        self.channels = {
            c : KeySight_EDU33212A_Channel(self._prot, c)
            for c in [1, 2]
        }

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
        # Keysight Technologies,EDU33212A,CN63210021,K-01.03.04-01.00-01.04-01.00-01.00
        return "EDU33212A" in output
    
    def open(self) -> None:
        """Open"""
        self._prot.open()

    def close(self) -> None:
        """Close"""
        self._prot.close()

    def channel(self, channel : int) -> KeySight_EDU33212A_Channel:
        """
        Return a single channel of the Keysight EDu33121A arbitrary waveform generator
        """
        if not (isinstance(channel, int) and 1 <= channel <= 2):
            raise ValueError(f'Invalid channel : {channel}')
        
        return self.channels[channel]
    
    def configure_sync_output(self,
                                state : bool,
                                source_channel : int,
                                mode : SyncMode = SyncMode.NORMAL,
                                polarity : Polarity = Polarity.NORMAL) -> None:
        """
        Configure the SYNC output
        Parameters
        ----------
        state : bool
            Enable / disables the sync output
        source_channel : int
        mode : SyncMode
        polarity : Polarity
        """
        assert isinstance(mode, SyncMode), f"Invalid mode type : {type(mode)}"
        assert isinstance(polarity, Polarity), f"Invalid polarity type : {type(polarity)}"

        self._prot.write(f'OUTP:SYNC:SOUR CH{source_channel}')
        self._prot.write(f'OUTP{source_channel}:SYNC:MODE {mode.value}')
        self._prot.write(f'OUTP{source_channel}:SYNC:POL {polarity.value}')
        self._prot.write(f'OUTP:SYNC {"ON" if state else "OFF"}')
