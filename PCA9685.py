#!/usr/bin/python

import time
import math
import smbus
import sys

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:

  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  def __init__(self, address=0x40, debug=False):
    self.bus = smbus.SMBus(1)
    self.address = address
    self.debug = debug
    if (self.debug):
      print("Reseting PCA9685")
    self.write(self.__MODE1, 0x00)
	
  def write(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    self.bus.write_byte_data(self.address, reg, value)
    if (self.debug):
      print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
	  
  def read(self, reg):
    "Read an unsigned byte from the I2C device"
    result = self.bus.read_byte_data(self.address, reg)
    if (self.debug):
      print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
	
  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
      print("Setting PWM frequency to %d Hz" % freq)
      print("Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
      print("Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    self.write(self.__PRESCALE, int(math.floor(prescale)))
    self.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.write(self.__MODE1, oldmode | 0x80)

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
    self.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
    if (self.debug):
      print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))
	  
  def setServoPulse(self, channel, pulse):
    "Sets the Servo Pulse,The PWM frequency must be 50HZ"
    pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us
    self.setPWM(channel, 0, int(pulse))

  def stop(self):
    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    # self.write(self.__MODE1, 0x00)

if __name__=='__main__':

  hor = 1500
  ver = 1500

  # range is 500-2500
  # 1500 : 90 deg

  if len(sys.argv) == 3:
     hor = int(sys.argv[1])
     ver = int(sys.argv[2])
  if len(sys.argv) == 2:
     # read the file
     text_file = open("/home/pi/pisolar/servos90.txt")
     hor = int(text_file.readline())
     ver = int(text_file.readline())
     text_file.close()
     print('hor: ' + str(hor) + ' ver: ' + str(ver))
     if sys.argv[1] == "Left":
         hor = hor + 50
         if hor > 2500:
            hor = 2500 
     elif sys.argv[1] == "Right":
         hor = hor - 50
         if hor < 500:
            hor = 500 
     elif sys.argv[1] == "Down":
         ver = ver + 50
         if ver > 2500:
            ver = 2500 
     elif sys.argv[1] == "Up":
         ver = ver - 50
         if ver < 500:
            ver = 500 
     else:
         print('hor: ' + str(hor) + ' ver: ' + str(ver))

  if hor > 2500 or hor < 500:
     hor = 1500
 
  if ver > 2500 or ver < 500:
     ver = 1500
 
  pwm = PCA9685(0x40, debug=True)
  pwm.setPWMFreq(50)
  pwm.setServoPulse(0,hor)   
  pwm.setServoPulse(1,ver)
  time.sleep(0.5)     

  # turning off servo
  pwm.stop()
  #pwm.set_PWM_dutycycle(servoh, 0)
  #pwm.set_PWM_frequency( servoh, 0 )

  #pwm.set_PWM_dutycycle(servov, 0)
  #pwm.set_PWM_frequency( servov, 0 )

  # save the value in a file
  text_file = open("/home/pi/pisolar/servos90.txt", "w")
  text_file.write(str(hor) + "\n")
  text_file.write(str(ver) + "\n")
  text_file.close()

