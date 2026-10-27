# Mercury communication changes

Work branch: vti/mercury-communications. The old OneDrive checkout is untouched.

- Construction no longer configures the iTC pressure loop or valve mode.
- The old behavior is available through explicit configure_manual_needle_valve().
- Getters consume one validated reply; no read-before-query buffer flush.
- SET acknowledgements are checked rather than ignored.
- Numeric parsing validates the terminal payload, including exponents and signed integers.
- In-process parameter transactions share a root-instrument RLock.
- Timeout is configurable through QCoDeS (seconds), default 2 seconds.
- Following a transport timeout/mismatched reply, close and recreate the driver session.
- Pressure setpoint and IPS heater properties return numbers.

Run `python -m pytest tests/test_mercury_communications.py` with the mercury/test extras.
The tests use simulated sockets and actual QCoDeS objects. They do not contact real hardware.
Existing raw write()/ask() access bypasses the parameter transaction helpers; do not use it concurrently.
Magnet control sequencing is inherited and still requires a separate control/safety review.
The localhost broker is supplied by the separate vti-control project, not this driver package.
No measurement environment was updated automatically. The update is published on the
`vti/mercury-communications` branch and proposed against `serial_comms` in draft PR
https://github.com/barreralab/BarreraLabDrivers/pull/4. It has not been merged.
