'''
Testing BarreraDCDAC driver with simulated instrument
Run by navigating to tests folder and executing 
pytest sim_test.py
'''

import pytest 

from barreralabdrivers import DCDAC5764
# The following decorator makes the driver
# available to all the functions in this module
@pytest.fixture(scope='function', name="dcdac_driver")
def _dcdac_driver():
    dcdac_sim = DCDAC5764('dcdac_sim',
                                 address='GPIB::1::INSTR',
                                 pyvisa_sim_file="DCDAC_5764.yaml")
    yield dcdac_sim

    dcdac_sim.close()


def test_init_v1(dcdac_driver):
    """
    Test that simple initialisation works
    """

    # There is not that much to do, really.
    # We can check that the IDN string reads back correctly

    idn_dict = dcdac_driver.IDN()

    assert idn_dict['vendor'] == 'BARRERA'
    assert idn_dict['model'] == 'DCDAC (Simulated)'