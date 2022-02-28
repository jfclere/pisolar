#!/usr/bin/python3
# Tell ATtiny to power off for a while.
import sys
import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte

DEVICE = 0x04 # Default device I2C address

bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0
def main():
    wait = int(sys.argv[1])
    # we can 0, 2, 4, 6 or 14
    if wait == 0 or wait == 2 or wait == 4 :
      # read val, batlow, batcharged
      bus.write_byte(DEVICE, wait)
      reply0 = int(bus.read_byte(DEVICE))
      reply1 = int(bus.read_byte(DEVICE))
      val = reply0 + (reply1 * 256)
      print(val)
    elif wait == 6 :
      # read stopfor (long)
      bus.write_byte(DEVICE, wait)
      reply0 = bus.read_byte(DEVICE)
      reply1 = bus.read_byte(DEVICE) 
      reply2= bus.read_byte(DEVICE) 
      reply3 = bus.read_byte(DEVICE) 
      val = ((reply3 * 256 + reply2)*256 + reply1) * 256 + reply0
      print(val)
    elif wait == 14:
      # read testmode
      bus.write_byte(DEVICE, wait)
      val = bus.read_byte(DEVICE)
      print(hex(val))

if __name__ == "__main__":
    main()
