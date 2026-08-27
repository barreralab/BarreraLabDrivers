import logging

from functools import partial
from typing import Any, Literal, Optional, Union

import qcodes.validators as vals
from qcodes.instrument import InstrumentChannel, InstrumentBase, InstrumentModule
from qcodes.parameters import ( DelegateParameter, create_on_off_val_mapping, Parameter )
from qcodes.validators import Bool, Enum, Ints, Numbers
from zhinst.qcodes import MFLI
from zhinst.qcodes import ZISession
import zhinst
import numpy as np
import typing as t

ModeType = Literal["CURR", "VOLT"]

log = logging.getLogger(__name__)


# class MagnitudeFromXY(Parameter):
#     def __init__(self, x_param, y_param, name='r', label='Magnitude', unit='V'):
#         super().__init__(name=name, label=label, unit=unit)
#         self._x = x_param
#         self._y = y_param

#     def get_raw(self):
#         x_val = self._x()
#         y_val = self._y()
#         return np.sqrt(x_val**2 + y_val**2)
    
# class PhaseFromXY(Parameter):
#     def __init__(self, x_param, y_param, name='phase', label='Phase', unit='deg'):
#         super().__init__(name=name, label=label, unit=unit)
#         self._x = x_param
#         self._y = y_param

#     def get_raw(self):
#         x_val = self._x()
#         y_val = self._y()
#         return np.degrees(np.arctan2(y_val, x_val))
    
# class DemodParameter(Parameter):
#     # Converts dictionary valued ZIParameter to a float valued qcodes parameter
#     def __init__(self, name, demod_sample_param, field, **kwargs):
#         super().__init__(name=name, **kwargs)
#         self._demod_sample_param = demod_sample_param
#         self._field = field

#     def get_raw(self):
#         sample = self._demod_sample_param()
#         return float(sample[self._field][0])

# # Define variables
# mfli_x = DemodParameter(
#     name='demod_x',
#     demod_sample_param=mfli.demods[0].sample,
#     field='x',
#     label='Demodulator X',
#     unit='V'
# )

# mfli_y = DemodParameter(
#     name='demod_y',
#     demod_sample_param=mfli.demods[0].sample,
#     field='y',
#     label='Demodulator Y',
#     unit='V'
# )

# mfli_freq = DemodParameter(
#     name='frequency',
#     demod_sample_param=mfli.demods[0].sample,
#     field='frequency',
#     label='Frequency',
#     unit='Hz'
# )

class SignalInput(InstrumentModule):

    """
    This is the module for the Signal Input. Here, parameters for input range, differential mode, AC coupling, input impedance are defined
    """

    def __init__(self, parent: 'MFLI_Instrument', name: str = 'SigIn'):
        """
        parent: The parent class which SignalInput is a child of. Allows usage of MFLI.SigIn.method()
        name: Str whcih is an argument for the Qcodes InstrumentModule class
        """
        super().__init__(parent, name)
        self.channel = 'SigIn'

        self.voltrange = Parameter(
            name = 

        )

class MFLI_Instrument(InstrumentBase):

    def __init__(
        self, 
        name: str, 
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
        ):

        """QCoDeS driver for the Zurich Instruments MFLI.
            
                Args:
                    name: The qcodes str used to identify the instrument within the station
                    serial: Serial number of the device, e.g. *'dev12000'*.
                        The serial number can be found on the back panel of the instrument.
                    server_host: Host address of the data server (e.g. localhost)
                    server_port: Port number of the data server. If not specified the session
                        uses the default port. (default = 8004)
                    interface: Device interface (e.g. = "1GbE"). If not specified
                        the default interface from the discover is used.
                    name: Name of the instrument in qcodes.
                    raw: Flag if qcodes instance should only created with the nodes and
                        not forwarding the toolkit functions. (default = False)
                    new_session: By default zhinst-qcodes reuses already existing data
                        server session (within itself only), meaning only one session to a
                        data server exists. Setting the flag will create a new session.
                    allow_version_mismatch: if set to True, the connection to the data-server
                        will succeed even if the data-server is on a different version of LabOne.
                        If False, an exception will be raised if the data-server is on a
                        different version. (default = False)
            """
        
        super().__init__(name = name, metadata = None, label = None)
        # The init for the InstumentBase class in QCodes. I don't know what metadata and label do yet
        self.mfli = MFLI(serial = serial, host= host, port=8004, interface="1GbE", allow_version_mismatch=True)
        print(f'Connected to: Zurich Instruments MFLI session at serial:{serial}')



