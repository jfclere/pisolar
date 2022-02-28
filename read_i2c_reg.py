#!/usr/bin/python3
# Tell ATtiny to read a register
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
    reg = int(sys.argv[1])
    reply = bus.read_i2c_block_data(DEVICE, reg, 8)
    # reply = bus.read_byte(DEVICE)
    print(reply)



if __name__ == "__main__":
    main()
