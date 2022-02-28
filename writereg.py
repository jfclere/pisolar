#!/usr/bin/python3
# Tell ATtiny to power off for a while.
from struct import *
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
    if wait == 2 or wait == 4 :
      # write batlow, batcharged
      val = int(sys.argv[2])
      mybytes = val.to_bytes(2, byteorder='little')
      data = unpack('BB', mybytes)
      data = [ mybytes[0], mybytes[1] ]
      print(data)
      bus.write_i2c_block_data(DEVICE, wait, data)
    elif wait == 6 :
      # write stopfor (long)
      val = int(sys.argv[2])
      mybytes = val.to_bytes(8, byteorder='little')
      data = unpack('BBBBBBBB', mybytes)
      data = [ mybytes[0], mybytes[1], mybytes[2], mybytes[3], mybytes[4], mybytes[5], mybytes[6], mybytes[7] ]
      print(data)
      bus.write_i2c_block_data(DEVICE, wait, data)
    elif wait == 14:
      # write testmode
      val = int(sys.argv[2])
      mybytes = val.to_bytes(1, byteorder='little')
      data = unpack('B', mybytes)
      data = [ mybytes[0] ]
      bus.write_i2c_block_data(DEVICE, wait, data)

if __name__ == "__main__":
    main()
