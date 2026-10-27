"""Shared Mercury transaction handling; connecting never configures hardware."""
import math
import re
import threading

_NUMBER = re.compile(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?)(?:[A-Za-z%/][A-Za-z%/0-9]*)?')

def response_float(response):
    match = _NUMBER.fullmatch(response.rsplit(':', 1)[-1])
    if not match:
        raise ValueError(f'Invalid numeric Mercury response: {response!r}')
    suffix = response.rsplit(':', 1)[-1][len(match[1]):]
    if suffix not in {'', 'K', 'T', 'mB', 'mbar', 'mBar', 'A', 'W', 'V', '%', 'T/m', 'T/min', 'Ohm', 'ohm', 'Hz'}:
        raise ValueError(f'Unrecognized numeric unit: {suffix!r}')
    value = float(match[1])
    if not math.isfinite(value):
        raise ValueError(f'Non-finite Mercury value: {response!r}')
    return value

class MercuryCommunication:
    def __init__(self, *args, **kwargs):
        self._mercury_lock = threading.RLock()
        self._mercury_desynchronized = False
        kwargs.setdefault('timeout', 2.0)  # QCoDeS timeout is in seconds.
        super().__init__(*args, **kwargs)

    def _mercury_query(self, command):
        with self._mercury_lock:
            if self._mercury_desynchronized:
                raise ConnectionError('Mercury session lost synchronization; close and recreate the instrument')
            try:
                reply = self.visa_handle.query(command).rstrip('\r\n')
            except Exception:
                self._mercury_desynchronized = True
                raise
            expected = 'IDN:' if command == '*IDN?' else 'STAT:' + command[5:] + ':'
            if not reply.startswith(expected):
                self._mercury_desynchronized = True
                raise ValueError(f'Mercury response mismatch for {command!r}: {reply!r}')
            if reply.rsplit(':', 1)[-1].upper() in {'INVALID', 'N/A', 'NAN', 'ERROR'}:
                raise ValueError(f'Mercury rejected query: {reply!r}')
            return reply

    def _mercury_set(self, command):
        with self._mercury_lock:
            if self._mercury_desynchronized:
                raise ConnectionError('Mercury session lost synchronization; close and recreate the instrument')
            try:
                reply = self.visa_handle.query(command).rstrip('\r\n')
            except Exception:
                self._mercury_desynchronized = True
                raise
            accepted = {'STAT:' + command + ':VALID', 'STAT:' + command, 'STAT:' + command[4:] + ':VALID'}
            if reply not in accepted:
                raise ValueError(f'Mercury SET not acknowledged: {reply!r}')
