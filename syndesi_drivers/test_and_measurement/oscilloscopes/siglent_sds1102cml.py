# Siglent SDS1102CML oscilloscope driver
# Sébastien Deriaz
# 30.05.2023

import re

from syndesi import Visa, Adapter, SerialPort, SCPIDriver, SCPI
from .oscilloscopes import MultiChannelOscilloscope, Coupling, OscilloscopeChannel

# ACQW : Specifi

class SDS1102CMLChannel(OscilloscopeChannel):
    """SDS1102CML Oscilloscope channel"""
    def __init__(self, protocol : SCPI, channel : int) -> None:
        super().__init__(channel)
        self._prot = protocol

    def set_coupling(self, coupling : Coupling | str):
        coupling = Coupling(coupling)
        coupling_match = {
            Coupling.AC : 'A1M',
            Coupling.DC : 'D1M',
            Coupling.GND : 'GND',
        }
        self._prot.write(f'C{self._channel}:CPL {coupling_match[coupling]}')

    def set_voltage_scale(self, volts_per_div : float):
        pass


class SDS1102CML(MultiChannelOscilloscope, SCPIDriver):
    """SDS1102CML Oscilloscope"""
    CHANGELOG = {
        "1.0.0" : "Initial version"
    }

    def __init__(self, adapter : Adapter) -> None:
        self._prot = SCPI(adapter)
        super().__init__(
            lambda channel : SDS1102CMLChannel(self._prot, channel),
            [1, 2]
        )

        assert isinstance(adapter, SerialPort) or isinstance(adapter, Visa), "Invalid adapter"

    def set_time_scale(self, seconds_per_div : float):
        pass

    def run_self_cal(self):
        """Run self-calibration"""
        out = self._prot.query('*CAL?')
        if out != '*CAL 0':
            raise RuntimeError('Self-calibration sequence failed, response : \'{out}\'')

    def read_error_register(self):
        """
        reads and clears the contents of
        the Command error Register (CMR)

        Returns
        -------
        code : int
        description : str
        """

        error_status_register_structure = {
            0 : 'No error',
            1 : 'Unrecognized command/query header',
            2 : 'Invalid character',
            3 : 'Invalid separator',
            4 : 'Missing parameter',
            5 : 'Unrecognized keyword',
            6 : 'String error',
            7 : 'Parameter cannot allowed',
            8 : 'Command String Too Long',
            9 : 'Query cannot allowed',
            10 : 'Missing Query mask',
            11 : 'Invalid parameter',
            12 : 'Parameter syntax error',
            13 : 'Filename too long'
        }
        out = self._prot.query('CMR?')
        # output is 'CMR x' with
        pattern = r'CMR [0-9]{1,2}'
        match = re.match(pattern, out)
        code = int(match.group(1))
        if code not in error_status_register_structure:
            raise ValueError('Invalid error code in response \'{out}\'')
        else:
            return code, error_status_register_structure[code]


    def save_csv(self):
        """
        TODO
        """
        pass

    def get_cymometer_value(self):
        """
        Queries the value of the cymometer
        When the signal frequency is less
        than 10Hz, it returns 10Hz.
        """
        out = self._prot.query('CYMOMETER?')
        # TODO : Convert 10Hz, 10kHz, 10Mhz, etc... to Hertz

    def force_trigger(self):
        """
        Causes the instrument to make one acquisition
        """
        self._prot.write('FORCE_TRIGGER')

    def set_filter_state(self, channel : int, state : bool):
        """
        Sets the filter state for the specified channel

        Parameters
        ----------
        channel : int
        state : bool
        """
        self._prot.write(f'C{channel}:FILT {"ON" if state else "OFF"}')


