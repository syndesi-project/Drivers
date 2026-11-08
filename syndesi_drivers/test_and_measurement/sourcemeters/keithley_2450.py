from syndesi import IP, Visa, SCPI, Driver

from syndesi_drivers.tools import NormalizedFloatStrEnum, NormalizedStrEnum

class CurrentRange(NormalizedFloatStrEnum):
    """Current range"""
    _10NA = 10e-9
    _100NA = 100e-9
    _1UA = 1e-6
    _10UA = 10e-6
    _100UA = 100e-6
    _1MA = 1e-3
    _10MA = 10e-3
    _100MA = 100e-3
    _1A = 1.000
    AUTO = "AUTO"

class VoltageRange(NormalizedFloatStrEnum):
    """Voltage range"""
    _20MV = 20e-3
    _200MV = 200e-3
    _2V = 2
    _20V = 20
    _200V = 200
    AUTO = "AUTO"

class SourceFunction(NormalizedStrEnum):
    """Source function"""
    VOLTAGE = 'voltage'
    CURRENT = 'current'

    @property
    def alias(self) -> str:
        """Return the source function alias for Keithley 2450"""
        if self.value == self.VOLTAGE.value:
            return 'VOLT'
        elif self.value == self.CURRENT.value:
            return 'CURR'
        else:
            raise ValueError("Invalid value")
        

class SenseFunction(NormalizedStrEnum):
    """Sense function"""
    VOLTAGE = 'VOLT'
    CURRENT = 'CURR'
    RESISTANCE = 'RES'

    @property
    def alias(self) -> str:
        """Return the sense function alias for Keithley 2450"""
        if self.value == self.VOLTAGE.value:
            return 'VOLT'
        elif self.value == self.CURRENT.value:
            return 'CURR'
        elif self.value == self.RESISTANCE.value:
            return 'RES'
        else:
            raise ValueError("Invalid value")

class Keithley2450(Driver):
    """
    Keithley 2450 SourceMeter unit

    Parameters
    ----------
    adpater : Adapter
    """
    def __init__(self, adapter: IP) -> None:
        super().__init__()

        assert isinstance(adapter, IP) or isinstance(adapter, Visa), "Invalid adapter"
        self._prot = SCPI(adapter, '\n')

    def open(self) -> None:
        self._prot.open()

    def close(self) -> None:
        self._prot.close()

    def test(self) -> bool:
        raise NotImplementedError()

    def set_output_state(self, state : bool) -> None:
        """
        Set the output state

        Parameters
        ----------
        state : bool
        """
        self._prot.write(f':OUTP {"ON" if state else "OFF"}')

    def set_source_function(self, function : str) -> None:
        """
        Set the source function : voltage or current

        Parameters
        ----------
        function : str
        """
        function = SourceFunction(function)
        self._prot.write(f':SOUR:FUNC {function.alias}')

    def get_source_function(self) -> SourceFunction:
        """
        Get the current source function

        Returns
        -------
        function : str
        """
        output = self._prot.query(':SOUR:FUNC?')
        return SourceFunction(output)

    def set_sense_function(self, sense_function : str) -> None:
        """
        Set the measurement function : voltage, current or resistance

        Parameters
        ----------
        function : str
        """
        self._prot.write(f'FUNC "{SenseFunction(sense_function).alias}"')

    def set_read_back_state(self, state : bool) -> None:
        """
        Enables or disables read back

            Disabled : The source value returned is the set source value (setpoint)
            Enabled : The source value returned is the measured value

        Parameters
        ----------
        state : bool
        """
        source_function = self.get_source_function()
        self._prot.write(f':SOUR:{source_function.alias}:READ:BACK {"ON" if state else "OFF"}')


    def set_current_source_amplitude(self, current : float, max_voltage : float | None = None) -> None:
        """
        Sets the current source amplitude

        Range : -1.05A to +1.05A

        If max_voltage is specified, the maximum current will be set

        Parameters
        ----------
        current : float
        max_voltage : float
        """
        if max_voltage is not None:
            self._prot.write(f':SOUR:CURR:VLIM {max_voltage:.6f}')
        self._prot.write(f':SOUR:CURR {current:.6f}')

    def set_current_sense_range(self, rng : CurrentRange) -> None:
        """
        Sets the current sensing range

        Any floating point value can be used, the instrument will
        determine automatically the appropriate range

        'AUTO' will put the device in auto mode

        Parameters
        ----------
        rng : CurrentRange
        """
        rng = CurrentRange(rng)
        if rng == CurrentRange.AUTO:
            self._prot.write(':CURR:RANG:AUTO ON')
        else:
            self._prot.write(f':CURR:RANG {rng.value}')


    def set_voltage_sense_range(self, rng : float | int | str) -> None:
        """
        Sets the voltage sensing range

        Any floating point value can be used, the instrument will
        determine automatically the appropriate range

        'AUTO' will put the device in auto mode

        Parameters
        ----------
        rng : float or str
        """
        rng = VoltageRange(rng)

        if rng == VoltageRange.AUTO:
            self._prot.write(':VOLT:RANG:AUTO ON')
        else:
            self._prot.write(f':VOLT:RANG {rng.value:.6e}')

    def set_voltage_source_amplitude(self, voltage : float | int, max_current : float | int | None = None) -> None:
        """
        Sets the voltage source amplitude

        Range : -210V to +210V

        If max_current is specified, the maximum current will be set

        Parameters
        ----------
        voltage : float
        max_current : float
        """
        if max_current is not None:
            self._prot.write(f':SOUR:VOLT:ILIM {max_current:.6e}')
        self._prot.write(f':SOUR:VOLT {voltage:.6e}')

    def set_front_terminals(self, enable : bool) -> None:
        """
        Enable or disables front/rear connectors

        Parameters
        ----------
        enable : bool
            True : Front terminals
            False : Rear terminals        
        """
        self._prot.write(f':ROUT:TERM {"FRON" if enable else "REAR"}')

    def get_measurement(self, function : str) -> float:
        """
        Get a single measurement from the specified function : 'voltage',
        'current' or 'resistance'

        Parameters
        ----------
        function : str
        """
        function = SenseFunction(function)
        return float(self._prot.query(f':MEAS:{function.alias}?'))

    def set_current_source_range(self, rng : float | int | str) -> None:
        """
        Sets the current source range

        Any floating point value can be used, the instrument will
        determine automatically the appropriate range

        Fixed current source ranges are :
        10nA, 100nA, 1uA, 10uA, 100uA, 1mA, 10mA, 100mA, 1A

        'AUTO' will put the device in auto mode

        Parameters
        ----------
        rng : float or str
        """
        rng = CurrentRange(rng)
        if rng == CurrentRange.AUTO:
            self._prot.write('SOUR:CURR:RANG:AUTO ON')
        else:
            self._prot.write(f'SOUR:CURR:RANG {rng.value:.6e}')

    def set_voltage_source_range(self, rng : float | int | str) -> None:
        """
        Sets the voltage source range

        Any floating point value can be used, the instrument will
        determine automatically the appropriate range

        Fixed voltage source ranges are :
        20mV, 200mV, 2V, 20V, 200V

        'AUTO' will put the device in auto mode


        Parameters
        ----------
        rng : float or str
        """
        rng = VoltageRange(rng)

        if rng == VoltageRange.AUTO:
            self._prot.write('SOUR:VOLT:RANG:AUTO ON')
        else:
            self._prot.write(f'SOUR:VOLT:RANG {rng.value}')
