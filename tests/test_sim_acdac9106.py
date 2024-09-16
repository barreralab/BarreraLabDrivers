'''
Testing BarreraDCDAC driver with simulated instrument
Run by navigating to tests folder and executing 
pytest sim_test.py
'''
import pytest 

from barreralabdrivers.drivers import ACDAC9106


# The following decorator makes the driver
# available to all the functions in this module
@pytest.fixture(scope='function', name="acdac_driver")
def _acdac_driver():
    ac_dac_sim = ACDAC9106('acdac_sim',
                                 address='GPIB::1::INSTR',
                                 pyvisa_sim_file="barreralabdrivers.sims:ACDAC9106.yaml")
    yield ac_dac_sim

    ac_dac_sim.close()


def test_init_v1(acdac_driver):
    """
    Test that simple initialisation works
    """

    # There is not that much to do, really.
    # We can check that the IDN string reads back correctly

    idn_dict = acdac_driver.IDN()

    assert idn_dict['vendor'] == 'BARRERA'
    assert idn_dict['model'] == 'ACDAC (Simulated)'