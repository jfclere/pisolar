#!/usr/bin/python3
# For Seeed Grove Multichannel gas sensor V2.0.
# Looking in the https://github.com/Seeed-Studio/Seeed_Arduino_MultiGas
# to write that python stuff.
# The 4 sensors all return 32 bits values (4 bytes of data).
# //command (from Multichannel_Gas_GMXXX.h)
# the warm up is probably more than 30 minutes :-(
#define GM_102B 0x01 NO2
#define GM_302B 0x03 C2H5OH alcohol gas sensor
#define GM_502B 0x05 VOC volatile organic compound gas sensor
#define GM_702B 0x07 CO carbon monoxide gas sensor
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
WARMING_UP   = 0xFE
WARMING_DOWN = 0xFF


bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0

def getUint32(data, index):
  # return four bytes from data as an unsigned 32-bit value
  return (data[index+3] << 32) + (data[index+2] << 16) + (data[index+1] << 8) + data[index]

def convert(adc):
  # convert the value to ppm
  # float calcVol(uint32_t adc, float verf = GM_VERF, int resolution = GM_RESOLUTION)
  # #define GM_VERF 3.3
  # #define GM_RESOLUTION 1023
  return (adc * 3.3) / 1023.0

def warm(bus, on):
  if on:
    bus.write_byte(DEVICE, WARMING_UP)
  else:
    bus.write_byte(DEVICE, WARMING_DOWN)
    

def main():

  warm(bus, 1)
  data = bus.read_i2c_block_data(DEVICE, GM_102B, 4)
  no2 = getUint32(data, 0)
  print("no2 : " + str(convert(no2)) + " ppm!")
  data = bus.read_i2c_block_data(DEVICE, GM_302B, 4)
  alcohol = getUint32(data, 0)
  print("alcohol : " + str(convert(alcohol)) + " ppm!")
  data = bus.read_i2c_block_data(DEVICE, GM_502B, 4)
  voc = getUint32(data, 0)
  print("voc : " + str(convert(voc)) + " ppm!")
  data = bus.read_i2c_block_data(DEVICE, GM_702B, 4)
  co = getUint32(data, 0)
  print("co : " + str(convert(co)) + " ppm!")

if __name__=="__main__":
   main()
