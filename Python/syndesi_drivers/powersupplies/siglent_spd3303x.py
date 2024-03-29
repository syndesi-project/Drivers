# Siglent SPD3303X-E and SPD3303X power supply drivers
# Sébastien Deriaz
# 02.04.2023

from syndesi.protocols import SCPI
from ...powersupply import IMultiChannelPowersupplyDC
from syndesi.adapters import *

from enum import Enum

class SPD3303x(IMultiChannelPowersupplyDC):
    def __init__(self, adapter : IAdapter) -> None:
        super().__init__()

        assert isinstance(adapter, VISA) or isinstance(adapter, IP), "Invalid adapter"

        self._prot = SCPI(adapter)


    def _checkChannel(self, channel):
        assert channel in [1,2], f"Invalid channel number : {channel}"
    
    def _checkNumber(self, inputValue):
        assert isinstance(inputValue, int) or isinstance(inputValue, float), \
            f"Invalid input {inputValue} of type {type(inputValue)}"

    def setVoltage(self, channel : int, volts : float):
        self._checkChannel(channel)
        self._checkNumber(volts)
        self._prot.write(f'CH{channel}:VOLT {volts:.3f}\n')


    def getVoltage(self, channel : int) -> float:
        self._checkChannel(channel)
        self._prot.write(f'CH{channel}:VOLT?\n')
        output = self._prot.read()
        try:
            volts = float(output)
        except ValueError as e:
            volts = None
        
        return volts

    def setCurrent(self, channel : int, amps : float):
        self._checkChannel(channel)
        self._checkNumber(amps)
        self._prot.write(f'CH{channel}:CURR {amps:.3f}\n')

    def getCurrent(self, channel : int) -> float:
        self._checkChannel(channel)
        self._prot.write(f'CH{channel}:CURR?\n')
        output = self._prot.read()
        try:
            amps = float(output)
        except ValueError as e:
            amps = None
        
        return amps

    def setOutputState(self, channel : int, state : bool):
        self._checkChannel(channel)
        self._prot.write(f'OUTP CH{channel} {"ON" if state else "OFF"}')


    class OperationMode(Enum):
        INDEPENDENT = 0
        SERIES = 1
        PARALLEL = 2


    def setOperationMode(self, mode : OperationMode):
        """
        Set the operation mode using the OperationMode enum class
        """

        assert isinstance(mode, self.OperationMode), "Invalid operation mode type"
        self._prot.write(f'OUTP:TRACK {mode.value}')

    def setWaveDisplay(self, channel : int, state : bool):
        """
        Enable/disable the wave display for the selected channel
        """
        self._checkChannel(channel)
        self._prot.write(f'OUTP:WAVE CH{channel},{"ON" if state else "OFF"}')

