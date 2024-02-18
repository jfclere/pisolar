#!/usr/bin/python3
# For Seeed Grove Multichannel gas sensor V2.0.
# Looking in the https://github.com/Seeed-Studio/Seeed_Arduino_MultiGas
# to write that python stuff.
# The 4 sensors all return 32 bits values (4 bytes of data).
# //command (from Multichannel_Gas_GMXXX.h)
#define GM_102B 0x01
#define GM_302B 0x03
#define GM_502B 0x05
#define GM_702B 0x07
#define CHANGE_I2C_ADDR 0x55
#define WARMING_UP 0xFE
#define WARMING_DOWN  0xFF
#

import smbus

DEVICE  = 0x08 # Default device I2C address
GM_102B = 0x01
GM_302B = 0x03
GM_502B = 0x05
GM_702B = 0x07


bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0

def getUint32(data, index):
  # return four bytes from data as an unsigned 32-bit value
  return (data[index+3] << 32) + (data[index+2] << 16) + (data[index+1] << 8) + data[index]

def main():

  data = bus.read_i2c_block_data(DEVICE, GM_102B, 4)
  gas1 = getUint32(data, 0)
  print("Gas1 : " + str(gas1) + " WhatEver!")
  data = bus.read_i2c_block_data(DEVICE, GM_302B, 4)
  gas1 = getUint32(data, 0)
  print("Gas1 : " + str(gas1) + " WhatEver!")
  data = bus.read_i2c_block_data(DEVICE, GM_502B, 4)
  gas1 = getUint32(data, 0)
  print("Gas1 : " + str(gas1) + " WhatEver!")
  data = bus.read_i2c_block_data(DEVICE, GM_702B, 4)
  gas1 = getUint32(data, 0)
  print("Gas1 : " + str(gas1) + " WhatEver!")

if __name__=="__main__":
   main()
