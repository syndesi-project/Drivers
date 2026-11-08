"""Siglent SDM3055 Driver"""

from syndesi import Adapter

from syndesi_drivers.tools import NormalizedFloatStrEnum
from .siglent_sdm30x5 import AUTO_RANGE, SiglentSDM30x5

class VoltageRange(NormalizedFloatStrEnum):
    """Voltage range"""
    _200MV = '200mV'
    _2V = '2V'
    _20V = '20V'
    _200V = '200V'
    _1000V = '1000V'
    AUTO = AUTO_RANGE

class ACVoltageRange(NormalizedFloatStrEnum):
    """AC Voltage range"""
    _200MV = '200mV'
    _2V = '2V'
    _20V = '20V'
    _200V = '200V'
    _750V = '750V'
    AUTO = AUTO_RANGE

class CurrentRange(NormalizedFloatStrEnum):
    """DC Current range"""
    _200UA = '200uA'
    _2MA = '2mA'
    _20MA = '20mA'
    _200MA = '200mA'
    _2A = '2A'
    _10A = '10A'
    AUTO = AUTO_RANGE

class ACCurrentRange(NormalizedFloatStrEnum):
    "AC Current range"
    _20MA = '20mA'
    _200MA = '200mA'
    _2A = '2A'
    _10A = '10A'
    AUTO = AUTO_RANGE

class ResistanceRange(NormalizedFloatStrEnum):
    """Resistance range"""
    _200 = '200'
    _2K = '2k'
    _20K = '20k'
    _200K = '200k'
    _2M = '2M'
    _10M = '10M'
    _100M = '100M'
    AUTO = AUTO_RANGE

class CapacitanceRange(NormalizedFloatStrEnum):
    _2NF = '2nF'
    _20NF = '20nF'
    _200NF = '200nF'
    _2UF = '2uF'
    _20UF = '20uF'
    _200UF = '200uF'
    _10MF = '10000uF'
    AUTO = AUTO_RANGE

class SiglentSDM3055(SiglentSDM30x5):
    """Siglent DM3055 Driver"""
    class NPLC(NormalizedFloatStrEnum):
        FAST = '0.3'
        MIDDLE = '1'
        SLOW = '10'

    def __init__(self, adapter: Adapter) -> None:
        super().__init__(adapter)
        self._model = 'SDM3055'
        self._ranges = {
            self.Function.VOLTAGE : self.VoltageRange,
            self.Function.VOLTAGE_AC : self.ACVoltageRange,
            self.Function.CURRENT : self.CurrentRange,
            self.Function.CURRENT_AC : self.CurrentRangeAC,
            self.Function.RESISTANCE : self.ResistanceRange,
            self.Function.RESISTANCE4 : self.ResistanceRange,
            self.Function.CAPACITANCE : self.CapacitanceRange
        }
        self._nplc = self.NPLC


class SDM3055(SiglentSDM30x5):
    """
    Siglent SDM3055 5½ digit multimeter

    Parameters
    ----------
    adpater : IAdapter
        Adapter to use, both IP and VISA are allowed
    """
    def __init__(self, adapter : Adapter) -> None:
        super().__init__()

        assert isinstance(adapter, IP) or isinstance(adapter, Visa), "Invalid adapter"
        self._prot = SCPI(adapter)

    def measure_ac_current(self) -> float:
        """
        Make an AC current measurement and return the result
        """
        self._prot.write('CONF:CURR:AC')
        self._prot.write('INIT')
        self._prot.write('*TRG')
        output = float(self._prot.query('FETC?'))
        return output

    def measure_dc_current(self) -> float:
        """
        Make a DC current measurement and return the result
        """
        self._prot.write('CONF:CURR:DC')
        self._prot.write('INIT')
        self._prot.write('*TRG')
        output = float(self._prot.query('FETC?'))
        return output

    def measure_ac_voltage(self) -> float:
        """
        Make an AC voltage measurement and return the result
        """
        self._prot.write('CONF:VOLT:AC')
        self._prot.write('INIT')
        self._prot.write('*TRG')
        output = float(self._prot.query('FETC?'))
        return output

    def measure_dc_voltage(self) -> float:
        """
        Make a DC voltage measurement and return the result
        """
        self._prot.write('CONF:VOLT:DC')
        self._prot.write('INIT')
        self._prot.write('*TRG')
        output = float(self._prot.query('FETC?'))
        return output