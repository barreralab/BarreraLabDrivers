"""
QCoDeS driver for the Bluefors LD250
written by Eames Donovan, Sam Paudel based on the drivers by eliasankerhold on https://github.com/eliasankerhold/BlueFTC
June 2026 revision 0.1: basic identification and read functionality
All functionality of the underlying BlueFTC is available via the bf.controller. .... method. 
Commonly measured or set parameters are wraped up as QCodes parameters. 
"""


import qcodes.validators as vals
import logging

from time import sleep
from typing import Any, Optional
from functools import partial
from qcodes.instrument import InstrumentModule, Instrument
from qcodes.parameters import Parameter
from qcodes.validators import Ints, Numbers, Bool
import re
from importlib import util
import numpy as np
import time
import sys
sys.path.append(
    r"C:\Users\barreralab\AppData\Roaming\Python\Python39\site-packages"
)
from blueftc.BlueforsController import BlueFTController

log = logging.getLogger(__name__)

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class BlueforsTemperatureController(Instrument):
    def __init__(
        self, 
        name: str, 
        configpath: str,
    ) -> None:
        """
        Initializes the controller. The controller python package is written by eliasankerhold

        name: str
        The qcodes name of the instrument. This is the name which will appear as a header of the .tsv from sweeping

        configpath: str
        The local path to the config file for the LD250. This contains file should contain the:
        ipaddress
        port
        key (API key)
        channel IDs (ints for identifying each thermometer, heater in the BF LD250 instrument collection)
        """

        super().__init__(name=name)
        self._load_config(configpath)

        self.controller = BlueFTController(ip= self._config.IP_ADDRESS, 
                                        port= self._config.PORT_NUMBER, 
                                        key= self._config.API_KEY, 
                                        mixing_chamber_channel_id= self._config.MXC_ID, 
                                        mixing_chamber_heater_id= self._config.MXC_HTR_ID,
                                        )

        self.add_submodule(name = 'mxc',
                           submodule = TemperatureModule(name = 'mxc', 
                                                         parent = self, 
                                                         temp_id= self._config.MXC_ID,
                                                         htr_id= self._config.MXC_HTR_ID,
                                                         ),
                            )

        self.add_submodule(name = 'fse',
                                   submodule = TemperatureModule(name = 'fse', 
                                                                 parent = self, 
                                                                 temp_id= self._config.FSE_ID,
                                                                 htr_id= self._config.FSE_HTR_ID,
                                                                 ),
                                    )

        self.add_submodule(name = 'still',
                                   submodule = TemperatureModule(name = 'still', 
                                                                 parent = self, 
                                                                 temp_id= self._config.STILL_ID,
                                                                 htr_id= self._config.STILL_HTR_ID,
                                                                 ),
                                    )

    def _load_config(self, configpath: str) -> None:
        """
        This helper function imports all of the variables from the config file specified by the configpath.
        The variables can be accessed by ._config.FIFTYK_ID, etc.
        """
        self._config_path = configpath
        spec = util.spec_from_file_location('Config Variables', configpath)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._config = module


class TemperatureModule(InstrumentModule):
    """
    This is a generic temperature module which reads the temperature/ heater of a system in the LD250
    Defines the .temp, .htr, .tloopmode methods
    """
    def __init__(self,
                 name: str,
                 parent: Instrument,
                 temp_id: int,
                 htr_id: int,
                 ):
        """
        name: str 
        the name used to identify the temperature module in QCodes stations (for example, mxc)

        parent: Intrument
        the class which this TemperatureModule is a part of (Usage BlueFors.mxc.temp())

        tempId: int,
        This is an integer identifier which distinguishes the thermometer in the Bluefors Frontened software. 
        The IDs are specified via the config file which is inherited from the parent
        """

        super().__init__(parent, name)
        self.temp_id = temp_id
        self.htr_id = htr_id
        self.controller = parent.controller
        if name == 'fse':
            self.unit = 'bftc2'
        else:
            self.unit = 'bftc'

        self.temp = Parameter(
            name = 'temp',
            unit = 'K',
            label = f'Temperature of {self.name}',
            get_cmd = lambda: self.controller.get_channel_temperature(self.temp_id),
            get_parser = float
        )

        """
        Only the still, mxc, and fse have heaters
        """
        if self.name == 'mxc' or 'fse' or 'still':

            self.active = Parameter(
                    name = 'active',
                    label = f'activate heater for {self.name}',
                    get_cmd = lambda: self._get_htr_attribute(htr_id = self.htr_id, target = "active"),
                    set_cmd = lambda x: self._set_htr_attribute(htr_id = self.htr_id, target = "active", value = self._parse_bools(x)),
                    get_parser = bool,
                )

            self.power = Parameter(
                name = 'heaterpower',
                unit = 'W',
                label = f'Heat power of {self.name}',
                get_cmd = lambda: self._get_htr_attribute(htr_id = self.htr_id, target = "power"),
                set_cmd = lambda x: self._set_htr_attribute(htr_id = self.htr_id, target = "power", value = x),
                get_parser = float,
            )

            self.setpoint = Parameter(
                name = 'setpoint',
                unit = 'K',
                label = f'Temperature setpoint for PID control of {self.name}',
                get_cmd = lambda: self._get_htr_attribute(htr_id = self.htr_id, target = "setpoint"),
                set_cmd = lambda x: self._set_htr_attribute(htr_id = self.htr_id, target = "setpoint", value = x),
                get_parser = float,
            )

            self.pid_mode = Parameter(
                name = 'pid_mode',
                label = f'Temperature pid_mode for PID control of {self.name}',
                get_cmd = lambda: self._get_htr_attribute(htr_id = self.htr_id, target = "pid_mode"),
                set_cmd = lambda x: self._set_htr_attribute(htr_id = self.htr_id, target = "pid_mode", value = self._parse_bools(x)),
                get_parser = bool,
            )

            self.pid_p = Parameter(
                name = 'pid_p',
                label = f'Temperature pid_p for PID control of {self.name}',
                get_cmd = lambda: self._get_htr_attribute(htr_id = self.htr_id, target = "pid_p"),
                set_cmd = lambda x: self._set_htr_attribute(htr_id = self.htr_id, target = "pid_p", value = x),
                get_parser = float,
            )

            self.pid_i = Parameter(
                name = 'pid_i',
                label = f'Temperature pid_i for PID control of {self.name}',
                get_cmd = lambda: self._get_htr_attribute(htr_id = self.htr_id, target = "pid_i"),
                set_cmd = lambda x: self._set_htr_attribute(htr_id = self.htr_id, target = "pid_i", value = x),
                get_parser = float,
            )

            self.pid_d = Parameter(
                name = 'pid_d',
                label = f'Temperature pid_d for PID control of {self.name}',
                get_cmd = lambda: self._get_htr_attribute(htr_id = self.htr_id, target = "pid_d"),
                set_cmd = lambda x: self._set_htr_attribute(htr_id = self.htr_id, target = "pid_d", value = x),
                get_parser = float,
            )


    def _get_htr_attribute(self, htr_id, target:str):
        """
        target is the name of the attribute we'd like to query
        valid targets are:

        "active"
        "power"
        "setpoint"
        "pid_mode"
        "pid_p"
        "pid_i"
        "pid_d"
        """
        device = f'driver.{self.unit}.data.heaters.heater_{htr_id}'
        data = self.controller._get_value_request(device, target)

        return float(
        self.controller._get_value_from_data_response(
        data,
        device=device,
        target= target
    )
    )

    def _set_htr_attribute(self, htr_id, target:str, value):
            """
            target is the name of the attribute we'd like to query
            valid targets are:
    
            "active"
            "power"
            "setpoint"
            "pid_mode"
            "pid_p"
            "pid_i"
            "pid_d"
            """
            print("SETTING:")
            print("  module:", self.name)
            print("  htr_id:", htr_id)
            print("  target:", target)
            print("  value:", value)
            device = f'driver.{self.unit}.data.heaters.heater_{htr_id}'
            print("  device:", device)
            self.controller._set_value_request(device, target, value)

    def _parse_bools(self,val):
        if val in (0, "off", False):
            return False
        elif val in (1, "on", True):
            return True
        else:
            raise ValueError(f"Invalid boolean value: {val}")
    
