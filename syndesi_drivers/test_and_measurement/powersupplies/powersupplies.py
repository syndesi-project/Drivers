from abc import abstractmethod
from typing import Any, Callable

from syndesi import SubDriver
from syndesi_drivers.test_and_measurement.instrument import MultiChannelInstrument

class DCPowerSupply(SubDriver):
    """
    Single channel power supply (or a specific channel of a multi-channel power supply)

    Parameters
    ----------
    channel_number : int
        Channel in the case of this instance being a specific channel of a multi-channel power supply (None by default)
    """
    def __init__(self, channel_number : int | None = None) -> None:
        super().__init__()
        self._channel_number = channel_number

    @abstractmethod
    def set_voltage(self, volts : float) -> None:
        """Set the power supply output voltage"""

    @abstractmethod
    def get_voltage(self) -> float:
        """Get power supply output voltage"""

    @abstractmethod
    def set_current(self, amps : float) -> None:
        """Set power supply max output current"""

    @abstractmethod
    def get_current(self) -> float:
        """Get power supply max output current"""

    @abstractmethod
    def set_output_state(self, state : bool) -> None:
        """Set power supply out state"""

    @abstractmethod
    def measure_voltage(self) -> float:
        """Measure power suplpy output voltage"""

    @abstractmethod
    def measure_current(self) -> float:
        """Measure power supply output current"""

class DCMultiChannelPowerSupply(MultiChannelInstrument):
    """
    A multi-channel DC power supply. Use .channel(int) to retrieve a channel
    """
    # Provides power supply functions (multi channel)

    def __init__(
            self,
            single_channel_creator: Callable[[int], Any],
            channels: list[int], pre_instanciate: bool = True
        ) -> None:
        super().__init__(single_channel_creator, channels, pre_instanciate)
