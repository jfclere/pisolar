#!/usr/bin/python3
# ocean 5V on gpio=23

import RPi.GPIO as GPIO
import os
import time
from nodeinfo import nodeinfo
from readreg import readreg
from writereg import writereg

OCEANGPIO=23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(OCEANGPIO,GPIO.OUT)
GPIO.output(OCEANGPIO,GPIO.LOW)

myinfo = nodeinfo()
if myinfo.read():
  print("Failed")
  exit()

if myinfo.TIME_ACTIVE > 0:
  GPIO.output(OCEANGPIO,GPIO.HIGH)
  print("on")
  time.sleep(60*myinfo.TIME_ACTIVE)

# end make sure to stop
GPIO.output(OCEANGPIO,GPIO.LOW)
