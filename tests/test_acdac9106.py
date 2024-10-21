import unittest

# import qcodes as qc
# from qcodes.extensions import DriverTestCase
import time
from barreralabdrivers.drivers import ACDAC9106


class TestDCDAC(unittest.TestCase):
    def setUp(self):
        self.acdac = ACDAC9106("dcdac", "ASRL6::INSTR")
        self.acdac.reset()

    def test_bad_values(self):
        for chan_num in range(4):
            self.assertRaises(ValueError, self._send_data, chan_num, -0.1)
            self.assertRaises(ValueError, self._send_data, chan_num, 451)

    def test_reset(self):
        self.acdac.reset()
        for chan in self.acdac.channels:
            self.assertAlmostEqual(chan.voltage(), 0, 3)

    # @unittest.skip("demonstrating skipping")
    def test_longevity(self):
        volts = []
        start_time = time.time()
        start = 0
        end = 450
        step = 10
        for volt in range(start, end, step):
            for chan in self.acdac.channels:
                chan.voltage(volt)
                meas = chan.voltage()
                if abs(meas - volt) > 0.0005:
                    print(f"Bad at {chan} with {volt}")
                volts.append(chan.voltage())
        end_time = time.time()

        ops = (end - start) / step * 4
        time_per_op = (end_time - start_time) / ops
        print(
            f"{end_time - start_time} seconds for {ops} operations -> {time_per_op}s/op"
        )

        self.assertLessEqual(time_per_op, 0.1)

    def _send_data(self, chan: int, val: float):
        self.acdac.channels[chan].voltage(val)

    def _get_data(self, chan: int):
        return self.acdac.channels[chan].voltage()

    def tearDown(self) -> None:
        self.acdac.close()


if __name__ == "__main__":
    unittest.main()
