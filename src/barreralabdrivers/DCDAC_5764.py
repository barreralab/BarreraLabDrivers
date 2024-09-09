import qcodes.validators as vals
import logging

from time import sleep
from typing import Any, Optional
from functools import partial
from qcodes.instrument import InstrumentChannel, VisaInstrument
from qcodes.parameters import ( Parameter )
from qcodes.validators import Ints, Numbers


log = logging.getLogger(__name__)


class DCDAC5764Channel(InstrumentChannel):
    """
    Class to hold one of the 8 DC DAC Channels
    """

    def __init__(self, parent: "DCDAC5764", name: str, channel: str) -> None:
        """
        Args:
            parent: The BarreraDCDAC5764 instance to which the channel is
                to be attached.
            name: The 'colloquial' name of the channel
            channel: The name used by the DCDAC, i.e. either
                'channel1', 'channel2', ..., 'channel8'
        """
        valid_chnls = [f"channel{i}" for i in range(1, 9)]
        if channel not in valid_chnls:
            raise ValueError(f'{channel} not in channel1, ..., channel8')

        super().__init__(parent, name)
        self.channel = channel
        self._extra_visa_timeout = 5000

        self.voltage: Parameter = self.add_parameter(
            name="voltage",
            unit="V",
            label="Voltage",
            get_parser=float,
            get_cmd=partial(self._get_set_voltage),
            set_cmd=partial(self._get_set_voltage),
            vals=Numbers(-10, 10)
            )
        "Voltage level parameter"

        self.offset: Parameter = self.add_parameter(
            name = "offset",
            label="Offset",
            get_cmd=False,
            set_cmd=f"{self.channel}:OFFSET {{}}",
            # signed 8 bit integer
            vals=Ints(-128, 127),
            )
        "Offset level settable parameter"

        self.step: Parameter = self.add_parameter(
            name="step",
            label="Step",
            get_cmd=False,
            set_cmd=f"{self.channel}:STEP {{}}",
            # signed 6 bit integer 
            vals=Ints(-32, 31)
            )
        "Step size settable parameter"

    def _get_set_voltage(self, voltage: Optional[float] = None) -> Optional[float]:
        """
        Get or set the voltage level.

        Args:
            voltage: If missing, we assume that we are getting the 
            current level. Else we are setting it
        """
        if voltage is not None:
            self.write(f'{self.channel}:VOLTAGE {voltage}')
        else:
            return self.ask(f'{self.channel}:VOLTAGE?')



class DCDAC5764(VisaInstrument):
    """
    QCoDeS driver for custom made DC-DAC AD55706 DC generator
    Args:
      name: What this instrument is called locally.
      address: The visa resource address of this instrument
      kwargs: kwargs to be passed to VisaInstrument class
      terminator: read terminator for reads/writes to the instrument.
    """

    def __init__(self, name: str, address: str, terminator: str = "\n", **kwargs: Any
    ) -> None:
        super().__init__(name, address, terminator=terminator, **kwargs)

        self.channels: list[DCDAC5764Channel] = []
        for ch in range(1, 9):
            ch_name = f"channel{ch}"
            channel = DCDAC5764Channel(self, ch_name, ch_name)
            self.add_submodule(ch_name, channel)
            self.channels.append(channel)

        # Required as Arduino takes around 2 seconds to setup serial
        sleep(3)
        self.connect_message()


    def reset(self) -> None:
        """
        Reset DAC to 0V on each channel, and sets offsets/steps to 0
        """
        self.write("*RST")
        for channel_num in range(8):
            inst_chnl = self.channels[channel_num]
            inst_chnl.offset(0)
            inst_chnl.step(0)
        log.debug("Reset Instrument. Re-querying settings...")
        self.snapshot(update=True)