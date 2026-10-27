import socketserver
import threading
import time
import concurrent.futures
import importlib.util
from pathlib import Path
import sys
import types
import pytest
DRIVERS=Path(__file__).resolve().parents[1]/'src/barreralabdrivers/drivers'

class Simulator(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    def __init__(self):
        self.commands = []
        self.bad_once, self.drop_once, self.delay_once = False, False, False
        super().__init__(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.serve_forever, daemon=True)
        self.thread.start()
    def close(self):
        self.shutdown(); self.server_close(); self.thread.join()

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            cmd = line.decode().strip()
            self.server.commands.append(cmd)
            if self.server.drop_once:
                self.server.drop_once = False
                return
            if self.server.delay_once:
                self.server.delay_once = False
                time.sleep(.3)
            if cmd == '*IDN?':
                reply = 'IDN:OXFORD INSTRUMENTS:MERCURY ITC:SIM:1'
            elif cmd == 'READ:SYS:CAT':
                reply = 'STAT:SYS:CAT:DEV:DB8.T1:TEMP:DEV:DB3.H1:HTR:DEV:DB5.P1:PRES:DEV:GRPZ:PSU'
            elif cmd.startswith('SET:'):
                reply = 'STAT:' + cmd + ':VALID'
            else:
                value = ''
                if cmd.endswith(':NICK'): value = cmd.split(':')[2]
                elif cmd.endswith(':SIG:TEMP'): value = '-1.2E-3K'
                elif cmd.endswith(':SIG:POWR'): value = '2.5W'
                elif cmd.endswith(':SIG:PRES'): value = '9.0mB'
                elif cmd.endswith(':ENAB'): value = 'OFF'
                elif cmd.endswith(':SIG:SWHT'): value = 'OFF'
                elif cmd.endswith(':SIG:CURR'): value = '0.0A'
                elif cmd.endswith(':SIG:RFLD'): value = '0.0T/m'
                elif cmd.endswith(':SIG:FLD'): value = '0.0T'
                elif cmd.endswith(':SIG:PFLD'): value = '3.0T'
                elif cmd.endswith(':ACTN'): value = 'HOLD'
                elif cmd.endswith(':STAT'): value = '40000000'
                if self.server.bad_once:
                    self.server.bad_once = False
                    value = 'INVALID'
                reply = 'STAT:' + cmd[5:] + ':' + value
            try:
                self.wfile.write((reply+'\n').encode());self.wfile.flush()
            except OSError:
                return


package = types.ModuleType('mercury_test_drivers')
package.__path__ = [str(DRIVERS)]
sys.modules['mercury_test_drivers'] = package

def load(filename):
    name='mercury_test_drivers.'+filename
    spec=importlib.util.spec_from_file_location(name,DRIVERS/(filename+'.py'))
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

ITC=load('OxfordMercuryITC').MercuryiTC
IPS=load('OxfordMercuryIPS').MercuryiPS

@pytest.mark.parametrize('klass',[ITC,IPS])
def test_qcodes_connect_has_no_writes_and_validates_queries(klass):
    sim=Simulator()
    instrument=None
    try:
        instrument=klass('test_mercury',f'TCPIP::127.0.0.1::{sim.server_address[1]}::SOCKET',visalib='@py',timeout=.3)
        assert instrument.visa_handle.timeout==300
        assert not any(c.startswith('SET:') for c in sim.commands)
        param=instrument.probe.temp if klass is ITC else instrument.mag.temp
        assert param()==-.0012
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            assert all(v==-.0012 for v in pool.map(lambda _:param(),range(8)))
        sim.bad_once=True
        with pytest.raises(ValueError):param()
        assert param()==-.0012
        if klass is ITC:
            instrument.configure_manual_needle_valve()
            assert sum(c.startswith('SET:') for c in sim.commands)==3
            assert isinstance(instrument.vti.pset.get_parser('STAT:DEV:DB5.P1:PRES:LOOP:PSET:3mB'),float)
    finally:
        if instrument:instrument.close()
        sim.close()
