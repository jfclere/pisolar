#!/usr/bin/python3
# Write in the ATtiny registers
from struct import *
import sys
import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte

DEVICE = 0x04 # Default device I2C address
class writereg:


  def __init__(self):
    self.bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                       # Rev 1 Pi uses bus 0
  def write(self, wait, val):
    # we can 0, 2, 4, 6, 8 or 16
    if wait == 2 or wait == 4 :
      # write batlow, batcharged
      mybytes = val.to_bytes(2, byteorder='little')
      data = unpack('BB', mybytes)
      data = [ mybytes[0], mybytes[1] ]
      self.bus.write_i2c_block_data(DEVICE, wait, data)
      return(data)
    elif wait == 8 :
      # write stopfor (long)
      mybytes = val.to_bytes(8, byteorder='little')
      data = unpack('BBBBBBBB', mybytes)
      data = [ mybytes[0], mybytes[1], mybytes[2], mybytes[3], mybytes[4], mybytes[5], mybytes[6], mybytes[7] ]
      self.bus.write_i2c_block_data(DEVICE, wait, data)
      return(data)
    elif wait == 16:
      # write testmode
      mybytes = val.to_bytes(1, byteorder='little')
      data = unpack('B', mybytes)
      data = [ mybytes[0] ]
      self.bus.write_i2c_block_data(DEVICE, wait, data)
      return(data)

if __name__ == "__main__":
    wait = int(sys.argv[1])
    val = int(sys.argv[2])
    at = writereg()
    data = at.write(wait, val)
    print(data)
