
from syndesi import SerialPort, Delimited
from .powersupplies import DCPowerSupply

class Tenma_72_13360(DCPowerSupply):
    def __init__(self, adapter: SerialPort) -> None:
        """
        Tenma 72-13360 30V 15A power supply

        Parameters
        ----------
        adpater : Adapter
        """
        super().__init__()

        assert isinstance(adapter, SerialPort), "Invalid adapter"
        self._prot = Delimited(adapter, termination='\n')

    def test(self) -> bool:
        """
        Test presence of the device
        """
        output = self._prot.query('*IDN?')
        # Output is typically :
        # Tenma ID : TENMA 72-13360 V2.2 SN:000003343070
        return 'tenma' in output.lower()

    def set_current(self, amps: float) -> None:
        """
        Set the power supply current
        
        Parameters
        ----------
        amps : float
        """
        self._prot.write(f'ISET:{amps}')

    def get_current(self) -> float:
        """
        Get the current setpoint

        Returns
        -------
        amps : float
        """
        return float(self._prot.query('ISET?'))

    def set_voltage(self, volts: float) -> None:
        """
        Set the power supply voltage
        
        Parameters
        ----------
        volt : float
        """
        self._prot.write(f'VSET:{float(volts):.3f}')

    def get_voltage(self) -> float:
        """
        Get the voltage setpoint

        Returns
        -------
        volts : float
        """
        return float(self._prot.query('VSET'))

    def measure_current(self) -> float:
        """
        Return the output current measurement

        Returns
        -------
        amps : float
        """
        return float(self._prot.query('IOUT?'))

    def measure_voltage(self) -> float:
        """
        Return the output voltage measurement

        Returns
        -------
        volts : float
        """
        return float(self._prot.query('VOUT?'))

    def set_beep_state(self, enabled : bool) -> None:
        """
        Enable or disable the beep

        Parameters
        ----------
        enabled : bool
        """
        self._prot.write(f'BOOP:{1 if enabled else 0}')

    def set_output_state(self, state: bool) -> None:
        """
        Set the output state

        Parameters
        ----------
        state : bool
        """
        self._prot.write(f'OUT:{1 if state else 0}')

    def set_overcurrent_protection(self, amps : float) -> None:
        """
        Set the overcurrent protection value

        Parameters
        ----------
        amps : float
        """
        self._prot.write(f'OCP:{float(amps):.3f}')

    def set_overvoltage_protection(self, volts : float) -> None:
        """
        Set the overvoltage protection value

        Parameters
        ----------
        volts : float
        """
        self._prot.write(f'OVP:{float(volts):.3f}')

    def set_voltage_slope(self, slope : float) -> None:
        """
        Set the voltage slope as V/100us

        Parameters
        ----------
        slope : float        
        """
        # TODO : Implement
        raise NotImplementedError()

    def set_lock(self, enabled : bool) -> None:
        """
        Enable or disable the front panel lock

        Parameters
        ----------
        enabled : bool
        """
        self._prot.write(f'LOCK:{1 if enabled else 0}')

    def set_external_trigger(self, enabled : bool) -> None:
        """
        Enable or disable the external trigger

        Parameters
        ----------
        enabled : bool
        """
        self._prot.write(f'EXIT:{1 if enabled else 0}')
