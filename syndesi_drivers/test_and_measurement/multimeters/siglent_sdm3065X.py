from syndesi import Adapter

from syndesi_drivers.tools import NormalizedFloatStrEnum

from .siglent_sdm30x5 import AUTO_RANGE, SiglentSDM30x5


class SiglentSDM3065X(SiglentSDM30x5):
    class VoltageRange(NormalizedFloatStrEnum):
        _200mV = '200mV'
        _2V = '2V'
        _20V = '20V'
        _200V = '200V'
        _1000V = '1000V'
        AUTO = AUTO_RANGE

    class VoltageRangeAC(NormalizedFloatStrEnum):
        _200mV = '200mV'
        _2V = '2V'
        _20V = '20V'
        _200V = '200V'
        _750V = '750V'
        AUTO = AUTO_RANGE

    class CurrentRange(NormalizedFloatStrEnum):
        _200uA = '200uA'
        _2mA = '2mA'
        _20mA = '20mA'
        _200mA = '200mA'
        _2A = '2A'
        _10A = '10A'
        AUTO = AUTO_RANGE

    class CurrentRangeAC(NormalizedFloatStrEnum):
        _200uA = '200uA'
        _2mA = '2mA'
        _20mA = '20mA'
        _200mA = '200mA'
        _2A = '2A'
        _10A = '10A'
        AUTO = AUTO_RANGE

    class ResistanceRange(NormalizedFloatStrEnum):
        _200 = '200'
        _2k = '2k'
        _20k = '20k'
        _200k = '200k'
        _1M = '1M'
        _10M = '10M'
        _100M = '100M'
        AUTO = AUTO_RANGE

    class CapacitanceRange(NormalizedFloatStrEnum):
        _2nF = '2nF'
        _20nF = '20nF'
        _200nF = '200nF'
        _2uF = '2uF'
        _20uF = '20uF'
        _200uF = '200uF'
        _2mF = '2mF'
        _20mF = '20mF'
        _100mF = '100mF'
        AUTO = AUTO_RANGE

    class NPLC(NormalizedFloatStrEnum):
        _0005 = '0.005'
        _005 = '0.05'
        _05 = '0.5'
        _1 = '1'
        _10 = '10'
        _100 = '100'

    class Bandwidth(NormalizedFloatStrEnum):
        _3Hz = '3Hz'
        _20Hz = '20Hz'
        _200Hz = '200Hz'

    def __init__(self, adapter: Adapter) -> None:
        super().__init__(adapter)
        self._model = 'SDM3065X'
        self._ranges = {
            self.Function.VOLTAGE : self.VoltageRange,
            self.Function.VOLTAGE_AC : self.VoltageRangeAC,
            self.Function.CURRENT : self.CurrentRange,
            self.Function.CURRENT_AC : self.CurrentRangeAC,
            self.Function.RESISTANCE : self.ResistanceRange,
            self.Function.RESISTANCE4 : self.ResistanceRange,
            self.Function.CAPACITANCE : self.CapacitanceRange
        }
        self._nplc = self.NPLC