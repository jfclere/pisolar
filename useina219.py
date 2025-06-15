#!/usr/bin/env python
# pip3 install pi-ina219
# push to the i2c0 of zerow
from ina219 import INA219
from ina219 import DeviceRangeError
import sys
import requests
import time
from nodeinfo import nodeinfo

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
      # connect to the server to get our information
      info = nodeinfo()
      if info.read():
        print("Failed no info!")
        exit()
      headers = {'Content-type': 'text/plain'}
      url = "https://" + info.server + "/webdav/" + info.REMOTE_DIR + "/current.txt"
      # Loop displaying medium current
      max = 0.0
      min = 100.0
      ina = INA219(SHUNT_OHMS)
      ina.configure()
      while True:
        ma = ina.current()
        vl = ina.voltage()
        pw = ina.power()
        if max < ma:
          max = ma
        if min > ma:
          min = ma 
        print("Bus Current: " + str(round(ma,3)) + " mA" + " min " + str(round(min,3)) + " max " + str(round(max,3)))
        mess = "Current : " + str(round(ma,2)) + "\n"
        mess = mess + "Voltage : " + str(round(vl,2)) + "\n"
        mess = mess + "Power : " + str(round(pw,2))
        requests.put(url, data=mess, headers=headers, auth=(info.login, info.password))
        time.sleep(10)
