"""Oscilloscope interfaces"""

from abc import abstractmethod
from typing import Any, Callable

from syndesi import Driver, SubDriver

from syndesi_drivers.test_and_measurement.instrument import InstrumentChannel, MultiChannelInstrument
from ...tools import NormalizedStrEnum

class Coupling(NormalizedStrEnum):
    """Oscilloscope channel coupling"""
    DC = 'DC'
    AC = 'AC'
    GND = 'GND'

class OscilloscopeChannel(InstrumentChannel):
    """Single oscilloscope channel interface"""
    @abstractmethod
    def set_voltage_scale(self, volts_per_div : float) -> None:
        """Set channel voltage scale"""

    @abstractmethod
    def set_coupling(self, coupling : Coupling | str) -> None:
        """Set channel coupling"""

class SingleChannelOscilloscope(Driver):
    """Oscilloscope interface"""
    @abstractmethod
    def set_time_scale(self, seconds_per_div : float) -> None:
        """Set horizontal time scale"""

class MultiChannelOscilloscope(SingleChannelOscilloscope, MultiChannelInstrument):
    """Multi-channel oscilloscope"""
    def __init__(
            self,
            single_channel_creator: Callable[[int], Any],
            channels: list[int], pre_instanciate: bool = True
        ) -> None:
        super().__init__(single_channel_creator, channels, pre_instanciate)
