# File : siglent_sc1016.py
# Author : Sébastien Deriaz
# License : GPL

from syndesi import SubDriver, SCPI
from ..instrument import InstrumentChannel, MultiChannelInstrument
from ...tools import NormalizedStrEnum, NormalizedFloatStrEnum

class Function(NormalizedStrEnum):
    """Scanner card Function"""
    VOLTAGE = 'DCV'
    VOLTAGE_AC = 'ACV'
    CURRENT = 'DCI'
    CURRENT_AC = 'ACI'
    RESISTANCE = '2W'
    RESISTANCE4 = '4W'
    CAPACITANCE = 'CAP'
    FREQUENCY = 'FRQ'
    CONTINUITY = 'CONT'
    DIODE = 'DIO'
    TEMPERATURE = 'TEMP'

class VoltageRange(NormalizedFloatStrEnum):
    """Scanner card voltage range"""
    _200MV = 200e-3
    _2V = 2
    _20V = 20
    _200V = 200
    AUTO = "AUTO"

# Current range is fixed at 2A

class ResistanceRange(NormalizedFloatStrEnum):
    """Resistance range"""
    _200 = 200
    _2K = 2e3
    _20K = 20e3
    _200K = 200e3
    _2M = 2e6 # This is only for SDM3045X and SDM3055
    _1M = 1e6 # This is only for SDM3065X
    _10M = 10e6
    _100M = 100e6
    AUTO = "AUTO"

class CapacitanceRange(NormalizedFloatStrEnum):
    """Capacitance range"""
    _2NF = 2e-9
    _20NF = 20e-9
    _200NF = 200e-9
    _2UF = 2e-6
    _20UF = 20e-6
    _200UF = 200e-6
    _10MF = 10e-3
    AUTO = "AUTO"

class Speed(NormalizedStrEnum):
    """Acquisition speed"""
    SLOW = "SLOW" # 5 readings/s
    FAST = "FAST" # 50 readings/s

class Impedance(NormalizedFloatStrEnum):
    """Impedance range"""
    _10M = 10e6
    _10G = 10e9

class TemperatureTransducer(NormalizedStrEnum):
    """Temperature transducers"""
    RTD_PT100 = 'RTD,PT100'
    RTD_PT1000 = 'RTD,PT1000'
    THER_BITS90 = 'THER,BITS90'
    THER_EITS90 = 'THER,EITS90'
    THER_JITS90 = 'THER,JITS90'
    THER_KITS90 = 'THER,KITS90'
    THER_NITS90 = 'THER,NITS90'
    THER_RITS90 = 'THER,RITS90'
    THER_SITS90 = 'THER,SITS90'
    THER_TITS90 = 'THER,TITS90'

class Aperture(NormalizedFloatStrEnum):
    """Gate time of scan card frequency measurement mode"""
    _0_001 = 1e-3
    _0_01 = 10e-3
    _0_1 = 100e-3
    _1 = 1

CURRENT_RANGE = 2
    
class ScannerCardChannel(InstrumentChannel, SubDriver):
    def __init__(self, protocol : SCPI, channel: int) -> None:
        super().__init__(channel)
        self._prot = protocol

    def configure_voltage(
            self,
            *,
            dc : bool,
            switch : bool,
            voltage_range : VoltageRange | str | float | int,
            speed : Speed | str
        ) -> None:
        voltage_range = VoltageRange(voltage_range)
        speed = Speed(speed)
        mode = Function.VOLTAGE if dc else Function.VOLTAGE_AC
        self._prot.write(f'ROUT:CHAN {self._channel},{"ON" if switch else "OFF"}," \
                         f"{mode.value},{voltage_range.value:.3e},{speed.value}')

    def configure_current(
            self,
            *,
            dc : bool,
            switch : bool,
            speed : Speed | str
        ) -> None:
        speed = Speed(speed)
        mode = Function.CURRENT if dc else Function.CURRENT_AC
        self._prot.write(f'ROUT:CHAN {self._channel},{"ON" if switch else "OFF"}," \
                         f"{mode.value},{CURRENT_RANGE},{speed.value}')

    def configure_resistance(
            self,
            *,
            four_wire : bool,
            switch : bool,
            resistance_range : ResistanceRange | int,
            speed : Speed | str
        ) -> None:
        mode = Function.RESISTANCE4 if four_wire else Function.RESISTANCE
        

    def configure_capacitance(self, *, switch : bool, capacitance_range : CapacitanceRange | int | float | str):
        mode = Function.CAPACITANCE


    def configure_frequency(self, *, switch : bool, voltage_range : VoltageRange | str | float | int, speed : Speed | str):
        mode = Function.FREQUENCY


    def configure_continuity(self):
        CONTINUITY = 'CONT'
        DIODE = 'DIO'
        TEMPERATURE = 'TEMP'
    
    

    def set_function(self, channel : int, switch : bool, function : Function, range : Range, speed : Speed, autozero : bool = None, aperture : Aperture = None):
        """
        Configure scanner card channel parameters

        Parameters
        ----------
        channel : int
            1 to 15
        switch : bool
            Enable or disable the channel
        mode : ScannerCardFunction
            Function
        range : ScannerCardRange
        speed : Speed
        autozero : bool
            Auto-zero for DC voltage and current measurements
        aperture : Aperture
            Gate time for frequency / period measurements
        """
        if autozero is not None:
            ...
        if aperture is not None:
            aperture = self.Aperture(aperture)
            self._prot.write(f'ROUT:{function.value}:APER {aperture.value}')

class ScannerCard(MultiChannelInstrument):
    """SDM30x5 scanner card"""
    

    def __init__(self, protocol : SCPI) -> None:
        self._prot = protocol
        super().__init__(
            lambda channel : ScannerCardChannel(self._prot, channel),
            channels = list(range(1, 16)) # 1-15
        )

    #def autozero

    def is_installed(self):
        """
        Return True if the scanner card is installed, return False otherwise

        Returns
        -------
        installed : bool
        """
        return bool(int(self._prot.query('ROUT:STAT?')))

    def set_status(self, enabled : bool):
        """
        Enable or disable the scanner card

        Parameters
        ----------
        enabled : bool
        """
        self._prot.write(f'ROUT:SCAN {"ON" if enabled else "OFF"}')

    def set_start(self, start : bool):
        """
        Start or stop scanning card measurement

        Parameters
        ----------
        start : bool
        """
        self._prot.write(f'ROUT:STAR {"ON" if start else "OFF"}')

    def set__loop_mode(self, mode : str):
        """
        Configure scan card loop mode (scan or step)

        Parameters
        ----------
        mode : str
            'scan' or 'step'
        """
        self._prot.write(f'ROUT:FUNC {mode}')

    def set__delay(self, delay : float):
        """
        Configure scanner card delay

        Parameters
        ----------
        delay : float
            Delay in seconds
        """
        self._prot.write(f'ROUT:DEL {delay}')

    def set_cycle_count(self, count : int | str):
        """
        Set the number of scanning card cycle measurements

        Parameters
        ----------
        count : int or str
            integer or 'AUTO'
        """
        if isinstance(count, str) and count.lower() == 'auto':
            self._prot.write('ROUT:COUN:AUTO ON')
        else:
            self._prot.write(f'ROUT:COUN {count}')

    


    def set_limits(self, lower = None, upper = None):
        """
        Sets the upper and lower limits of the scanning card channel

        Parameters
        ----------
        lower : int
            1 to 15
        upper : int
            1 to 15
        """
        if lower is not None:
            self._prot.write(f'ROUT:LIM:LOW {lower}')
        if upper is not None:
            self._prot.write(f'ROUT:LIM:HIGH {upper}')

    def get_last_measurement(self, channel : int):
        """
        Return the final measurement value of the scan card channel

        Parameters
        ----------
        channel : int
            1 to 15
        """
        value = float(self._prot.query(f'ROUT:DATA? {channel}'))
        return value

    def set_relative_mode(self, function : Function, relative : bool):
        """
        Configure the relative value switch of the scanner card measurement function

        Parameters
        ----------
        function : Function
        relative : bool
        """
        self._prot.write(f'ROUT:RELA {function.value},{"ON" if relative else "OFF"}')

    def set_impedance(self, impedance : Impedance):
        """
        Set input impedance of the scanner card

        Parameters
        ----------
        impedance : Impedance
        """
        self._prot.write(f'ROUT:IMP {impedance.value}')

    def set_temperature_transducer(self, transducer : TemperatureTransducer):
        """
        Configure thermal resistance model

        Parameters
        ----------
        transducer : TemperatureTransducer
        """
        self._prot.write(f'ROUT:TEMP:{transducer.value}')

    def set_temperature_unit(self, unit : str):
        """
        Set temperature unit

        Parameters
        ----------
        unit : str
            'C', 'F' or 'K'
        """
        self._prot.write(f'ROUT:TEMP:UNIT {unit.upper()}')

    def set_frequency_display_mode(self, period : bool):
        """
        Set frequency or period display mode

        Parameters
        ----------
        period : bool
            True : Period mode
            False : Frequency mode
        """
        self._prot.write(f'ROUT:{"FREQ" if period else "PER"}')