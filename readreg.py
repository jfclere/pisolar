#!/usr/bin/python3
# Tell ATtiny to power off for a while.
import sys
import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte

DEVICE = 0x04 # Default device I2C address
class readreg:

  def __init__(self):
    self.bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                         # Rev 1 Pi uses bus 0
  def read(self, wait):
    wait = int(sys.argv[1])
    # we can 0, 2, 4, 6, 8 or 16
    if wait == 0 or wait == 2 or wait == 4 or wait == 6 :
      # read val, batlow, batcharged
      self.bus.write_byte(DEVICE, wait)
      reply0 = int(self.bus.read_byte(DEVICE))
      reply1 = int(self.bus.read_byte(DEVICE))
      val = reply0 + (reply1 * 256)
      return(val)
    elif wait == 8 :
      # read stopfor (long)
      self.bus.write_byte(DEVICE, wait)
      reply0 = self.bus.read_byte(DEVICE)
      reply1 = self.bus.read_byte(DEVICE) 
      reply2= self.bus.read_byte(DEVICE) 
      reply3 = self.bus.read_byte(DEVICE) 
      val = ((reply3 * 256 + reply2)*256 + reply1) * 256 + reply0
      return(val)
    elif wait == 16:
      # read testmode
      self.bus.write_byte(DEVICE, wait)
      val = self.bus.read_byte(DEVICE)
      return(hex(val))

if __name__ == "__main__":
    wait = int(sys.argv[1])
    at = readreg()
    val = at.read(wait)
    print(val)
