#!/usr/bin/env python
from ina219 import INA219
from ina219 import DeviceRangeError
import sys

SHUNT_OHMS = 0.1


def read():
    ina = INA219(SHUNT_OHMS)
    ina.configure()

    print("Bus Voltage: %.3f V" % ina.voltage())
    try:
        print("Bus Current: %.3f mA" % ina.current())
        print("Power: %.3f mW" % ina.power())
        print("Shunt voltage: %.3f mV" % ina.shunt_voltage())
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resistor
        print(e)

if __name__ == "__main__":
    print("main")
    args = sys.argv[1:]
    # args is a list of the command line args
    if len(args) == 0:
      read()
    else:
      # Loop displaying medium current
      i = 0
      t = 0
      max = 0.0
      min = 100.0
      ina = INA219(SHUNT_OHMS)
      ina.configure()
      while True:
        i = i + 1 
        v = ina.current()
        if max < v:
          max = v
        if min > v:
          min = v 
        t = t + v
        m = t/i
        print("Bus Current: " + str(round(m,3)) + " mA" + " min " + str(round(min,3)) + " max " + str(round(max,3)))
