from syndesi import Adapter

from syndesi_drivers.tools import NormalizedFloatStrEnum

from .siglent_sdm30x5 import SiglentSDM30x5, AUTO_RANGE

class SiglentSDM3045X(SiglentSDM30x5):
    class VoltageRange(NormalizedFloatStrEnum):
        _600mV = '600mV'
        _6V = '6V'
        _60V = '60V'
        _600V = '600V'
        _1000V = '1e3V'
        AUTO = AUTO_RANGE

    class VoltageRangeAC(NormalizedFloatStrEnum):
        _600mV = '600mV'
        _6V = '6V'
        _60V = '60V'
        _600V = '600V'
        _750V = '750V'
        AUTO = AUTO_RANGE

    class CurrentRange(NormalizedFloatStrEnum):
        _600uA = '600uA'
        _6mA = '6mA'
        _60mA = '60mA'
        _600mA = '600mA'
        _6A = '6A'
        _10A = '10A'
        AUTO = AUTO_RANGE

    class CurrentRangeAC(NormalizedFloatStrEnum):
        _60mA = '60mA'
        _600mA = '600mA'
        _6A = '6A'
        _10A = '10A'
        AUTO = AUTO_RANGE

    class ResistanceRange(NormalizedFloatStrEnum):
        _600 = '600'
        _6k = '6k'
        _60k = '60k'
        _600k = '600k'
        _6M = '6M'
        _60M = '60M'
        _100M = '100M'
        AUTO = AUTO_RANGE

    class CapacitanceRange(NormalizedFloatStrEnum):
        _2nF = '2nF'
        _20nF = '20nF'
        _200nF = '200nF'
        _2uF = '2uF'
        _20uF = '20uF'
        _200uF = '200uF'
        _10mF = '10000uF'
        AUTO = AUTO_RANGE

    class NPLC(NormalizedFloatStrEnum):
        FAST = '0.3'
        MIDDLE = '1'
        SLOW = '10'


    def __init__(self, adapter: Adapter) -> None:
        super().__init__(adapter)
        self._model = 'SDM3045X'
        self._ranges = {
            self.Function.VOLTAGE : self.VoltageRange,
            self.Function.VOLTAGE_AC : self.VoltageRangeAC,
            self.Function.CURRENT : self.CurrentRange,
            self.Function.CURRENT_AC : self.CurrentRangeAC,
            self.Function.RESISTANCE : self.ResistanceRange,
            self.Function.RESISTANCE4 : self.ResistanceRange,
            self.Function.CAPACITANCE : self.CapacitanceRange,
            self.Function.TEMPERATURE : self.TemperatureTransducer
        }
        self._nplc = self.NPLC