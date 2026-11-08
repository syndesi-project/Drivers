# File : instrument.py
# Author : Sébastien Deriaz
# License : GPL
from __future__ import annotations
from typing import Callable, Generic, TypeVar
from syndesi import SubDriver, Driver

SingleChannelT = TypeVar("SingleChannelT", bound=SubDriver)


SingleChannelArgsT = TypeVar("SingleChannelArgsT")

class MultiChannelInstrument(Generic[SingleChannelT], Driver):
    """
    An instrument that contains multiple channels. This class provides helper function to instanciate
    single channel classes
    """
    def __init__(
            self,
            single_channel_creator : Callable[[int], SingleChannelT],
            channels : list[int],
            pre_instanciate : bool = True
        ) -> None:
        self._channels = channels
        self._channel_instances : dict[int, SingleChannelT] = {}
        self._single_channel_creator = single_channel_creator

        if pre_instanciate:
            self._instanciate_all_channels()

    def channel(self, channel : int) -> SingleChannelT:
        """
        Return a single channel
        """
        if channel not in self._channels:
            raise ValueError(f"Channel '{channel}' is not a valid channel ({self._channels})")

        if channel not in self._channel_instances:
            self._channel_instances[channel] = self._single_channel_creator(channel)
        return self._channel_instances[channel]

    def _instanciate_all_channels(self):
        for channel in self._channels:
            if channel not in self._channel_instances:
                self._channel_instances[channel] = self._single_channel_creator(channel)

    @property
    def channels(self) -> list[SingleChannelT]:
        """List of channels"""
        self._instanciate_all_channels()
        return list(self._channel_instances.values())
    
class InstrumentChannel(SubDriver):
    """A single channel of a multi-channel instrument"""
    def __init__(self, channel : int) -> None:
        self._channel = channel
    
    # @abstractmethod
    # def open(self) -> None:
    #     """
    #     Open the driver and its protocols/adapters. Must be implemented
    #     by the user
    #     """

    # @abstractmethod
    # def close(self) -> None:
    #     """
    #     Close the driver and its protocols/adapters. Must be implemented
    #     by the user
    #     """

    # @abstractmethod
    # def test(self) -> bool:
    #     """
    #     Test communication with the target. Return True on success and False otherwise
    #     """
