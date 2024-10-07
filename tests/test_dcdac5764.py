import unittest

# import qcodes as qc
# from qcodes.extensions import DriverTestCase
import time
from barreralabdrivers import DCDAC5764


class TestDCDAC(unittest.TestCase):
    def setUp(self):
        self.dcdac = DCDAC5764("dcdac", "ASRL4::INSTR")
        self.dcdac.reset()
        self.dcdac

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

    def _send_data(self, chan: int, val: float):
        self.dcdac.channels[chan].voltage(val)

    def _get_data(self, chan: int):
        return self.dcdac.channels[chan].voltage()

    def tearDown(self) -> None:
        self.dcdac.close()


if __name__ == "__main__":
    unittest.main()
