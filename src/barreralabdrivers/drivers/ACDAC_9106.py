import qcodes.validators as vals
import logging

from time import sleep
from typing import Any, Optional
from functools import partial
from qcodes.instrument import InstrumentChannel, VisaInstrument
from qcodes.parameters import Parameter
from qcodes.validators import Ints, Numbers

log = logging.getLogger(__name__)


class ACDAC9106Channel(InstrumentChannel):
    """
    Class to hold one of the 4 AC DAC Channels
    """

    def __init__(self, parent: "ACDAC9106", name: str, channel: str) -> None:
        """
        Args:
            parent: The ACDAC instance to which the channel is
                to be attached.
            name: The 'colloquial' name of the channel
            channel: The name used by the DAC, i.e. either
                'ch1', 'ch2', 'ch3', or 'ch4'
        """
        valid_chnls = [f"ch{i}" for i in range(1, 9)]
        if channel not in valid_chnls:
            raise ValueError(f"{channel} not in ch1, ..., ch8")

        super().__init__(parent, name)
        self.channel = f"CHAN{channel[-1]}"
        self._extra_visa_timeout = 5000

        self.voltage: Parameter = self.add_parameter(
            name="voltage",
            unit="mV",
            label="Voltage",
            get_parser=float,
            get_cmd=partial(self._get_set_voltage),
            set_cmd=partial(self._get_set_voltage),
            vals=Numbers(0, 450),
        )
        "Voltage level parameter"

        self.phase: Parameter = self.add_parameter(
            name="phase",
            unit="deg",
            label="Phase",
            get_parser=float,
            get_cmd=f"{self.channel}:PHASE?",
            set_cmd=f"{self.channel}:PHASE {{}};PAT:UPDATE",
            vals=Numbers(-180, 180),
        )
        "Phase parameter"

    def _get_set_voltage(self, voltage: Optional[float] = None) -> Optional[float]:
        """
        Get or set the voltage level.

        Args:
            voltage: If missing, we assume that we are getting the
            current level. Else we are setting it
        """
        if voltage is not None:
            self.write(f"{self.channel}:VOLTAGE {voltage};PAT:UPDATE")
        else:
            return self.ask(f"{self.channel}:VOLTAGE?")


class ACDAC9106(VisaInstrument):
    """
    QCoDeS driver for custom made DC-DAC AD55706 DC generator
    Args:
      name: What this instrument is called locally.
      address: The visa resource address of this instrument
      kwargs: kwargs to be passed to VisaInstrument class
      terminator: read terminator for reads/writes to the instrument.
    """

    def __init__(
        self, name: str, address: str, terminator: str = "\n", **kwargs: Any
    ) -> None:
        super().__init__(name, address, terminator=terminator, **kwargs)

        self.channels: list[ACDAC9106Channel] = []
        for ch in range(1, 5):
            ch_name = f"ch{ch}"
            channel = ACDAC9106Channel(self, ch_name, ch_name)
            self.add_submodule(ch_name, channel)
            self.channels.append(channel)

        self.frequency: Parameter = self.add_parameter(
            name="frequency",
            unit="Hz",
            label="Frequency",
            get_parser=float,
            get_cmd=f"FREQ?",
            set_cmd=f"FREQ {{}};PAT:UPDATE",
            vals=Numbers(0, 1e6),
        )

        self.error: Parameter = self.add_parameter(
            name="error", label="Error", get_cmd="SYS:ERR?", set_cmd=False
        )

        self.display_mode: Parameter = self.add_parameter(
            name="display_mode",
            label="Display Mode",
            get_cmd=False,
            set_cmd=f"SYS:DISP:MODE {{}}",
            val_mapping={
                "NORMAL": 0,
                "FOCUS1": 1,
                "FOCUS2": 2,
                "FOCUS3": 3,
                "FOCUS4": 4,
                "REMOTE": 5,
            },
        )

        # Required as Arduino takes around 2 seconds to setup serial
        sleep(3)
        self.connect_message()

        # Set to remote access mode by default
        self.display_mode("REMOTE")

    def reset(self) -> None:
        """
        Reset DAC to 0V and 0deg phase on each channel
        """
        self.write("*RST")
        self.display_mode("REMOTE")
        log.debug("Reset Instrument. Re-querying settings...")
        self.snapshot(update=True)
