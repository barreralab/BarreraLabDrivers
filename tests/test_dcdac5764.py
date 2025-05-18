import unittest

# import qcodes as qc
# from qcodes.extensions import DriverTestCase
import time
import numpy as np
from barreralabdrivers.drivers import DCDAC5764
import random

address = "ASRL4::INSTR"


class TestDCDAC(unittest.TestCase):
    def setUp(self):
        self.dcdac = DCDAC5764("dcdac", address)
        self.dcdac.reset()

    # def test_add_station(self):
    #     station = qc.Station()
    #     try:
    #         station.add_component(self.dcdac)
    #     except

    def test_bad_values(self):
        for chan_num in range(8):
            self.assertRaises(ValueError, self._send_data, chan_num, -10.1)
            self.assertRaises(ValueError, self._send_data, chan_num, 10.1)

    def test_reset(self):
        self.dcdac.reset()
        for chan in self.dcdac.channels:
            self.assertAlmostEqual(chan.voltage(), 0, 3)

    @unittest.skip("demonstrating skipping")
    def test_longevity(self):
        volts = []
        start = time.time()
        for offset in range(0, 2):
            for step in range(0, 2):
                for volt in range(-10, 11):
                    for chan in self.dcdac.channels:
                        chan.offset(offset)
                        chan.step(step)
                        chan.voltage(volt)
                        meas = chan.voltage()
                        if abs(meas - volt) > 0.0005:
                            print(f"Bad at {chan} with {volt}")
                        volts.append(chan.voltage())
        end = time.time()

        time_per_op = (end - start) / (4 * 21 * 8)
        print(f"{end - start} seconds for {4 * 21 * 8} operations -> {time_per_op}s/op")

        self.assertLessEqual(time_per_op, 0.14)

    # @unittest.skip("demonstrating skipping")
    def test_paramp_single_chan(self):
        start = 10
        chan = self.dcdac.channels[random.randint(0, 7)]
        points = [(random.random() * 20 - 10) for _ in range(100)]
        for point in points:
            chan.voltage(point)
            believed = chan.voltage()
            self.assertAlmostEqual(point, believed, 3)

    def test_getting(self):
        for chan in self.dcdac.channels:
            self.assertAlmostEqual(chan.voltage(), 0, 3)

    def _send_data(self, chan: int, val: float):
        self.dcdac.channels[chan].voltage(val)

    def _get_data(self, chan: int):
        return self.dcdac.channels[chan].voltage()

    def tearDown(self) -> None:
        self.dcdac.close()


if __name__ == "__main__":
    unittest.main()
