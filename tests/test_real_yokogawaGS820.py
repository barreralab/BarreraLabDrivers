import unittest
from qcodes.extensions import DriverTestCase

from barreralabdrivers.drivers import YokogawaGS820

address = "TCPIP0::169.254.169.1::inst0::INSTR"

class TestYoko(unittest.TestCase):
    def setUp(self):
        self.yoko = YokogawaGS820("yoko820", address)
        self.yoko1 = self.yoko.channel1
        self.yoko2 = self.yoko.channel2
        self.yoko.reset()

    def test_set_modes_dual(self):
        self.yoko1.source_mode("CURR")
        self.yoko2.source_mode("VOLT")
        self.assertEqual(self.yoko1.source_mode(), "CURR")
        self.assertEqual(self.yoko2.source_mode(), "VOLT")

    def test_ramp_channel1(self):
        self.yoko1.source_mode("VOLT")
        self.yoko1.auto_range(1)
        self.yoko1.voltage(0)
        self.yoko1.ramp_voltage(10, 1, 0.5)
        self.assertAlmostEqual(self.yoko1.voltage(), 10)

    def test_ramp_channel2(self):
        self.yoko2.source_mode("CURR")
        self.yoko2.auto_range(1)
        self.yoko2.current(0)
        self.yoko2.ramp_current(0.1, 0.005, 0.5)
        self.assertAlmostEqual(self.yoko2.current(), 0.1)
        

    # def test_reset(self):
    #     for param in self.yoko.parameters
        
    def tearDown(self) -> None:
        self.yoko.close()

if __name__ == "__main__":
    unittest.main()
