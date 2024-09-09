import qcodes as qc

from barreralabdrivers import ACDAC9106
from time import sleep
dac = ACDAC9106("acdac", "ASRL5::INSTR")

station = qc.Station()

dac.reset()

station.add_component(dac)


dac.ch3.voltage(400)
dac.ch4.voltage(400)


dac.ch4.phase(24)

dac.display_mode("FOCUS4")

dac.print_readable_snapshot()

while True:
    volts = float(input("Enter voltage: "))
    if (volts < 0):
        break
    try:
        dac.ch4.voltage(volts)
    except ValueError:
        print("Invalid voltage")
    except:
        dac.error()

    print(dac.error())

for i in range(4):
    print(dac.channels[i].phase())

dac.frequency(24e3)


dac.close()
