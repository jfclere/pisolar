#!/usr/bin/python3
# ocean 5V on gpio=23

import RPi.GPIO as GPIO
import os
import time
from nodeinfo import nodeinfo
from readreg import readreg
from writereg import writereg
from reportserver import reportserver

OCEANGPIO=23

# update register of the ATtiny
def updatereg(nodeinfo, readreg):
  batlow = readreg.read(2)
  batcharged = readreg.read(4)
  setbatlow = nodeinfo.BAT_LOW
  setbatcharged = nodeinfo.BATCHARGED
  if setbatlow > 0 and setbatlow != batlow:
    print("batlow: " + str(batlow) + ":" + str(setbatlow))
    mywritereg = writereg()
    mywritereg.write(2, setbatlow)
  if setbatcharged > 0 and setbatcharged != batcharged:
    print("batcharged: " + str(batcharged) + ":" + str(setbatcharged))
    mywritereg = writereg()
    mywritereg.write(4, setbatcharged)

def stopatt(wait):
  mywritereg = writereg()
  mywritereg.write(8, wait)
  os.system("sudo init 0")
    

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(OCEANGPIO,GPIO.OUT)
GPIO.output(OCEANGPIO,GPIO.LOW)

myinfo = nodeinfo()
if myinfo.read():
  print("Failed")
  stopatt(500)
  exit()

if myinfo.TIME_ACTIVE > 0:
  GPIO.output(OCEANGPIO,GPIO.HIGH)
  print("on")
  time.sleep(60*myinfo.TIME_ACTIVE)

# end make sure to stop
GPIO.output(OCEANGPIO,GPIO.LOW)

# update register
myreg = readreg()
myreportserver = reportserver()
myreportserver.report(myinfo, myreg)
updatereg(myinfo, myreg)

# stop and wait
stopatt(myinfo. WAIT_TIME)
